package io.github.d3kstra.rag_knowledge_qa.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * 文档元数据服务：把「文档类型 / 适用范围 / 现行状态」注入 chunk 标签，让模型有能力裁决
 * "上下位文件冲突"（制度 vs 细则）与"主体错配"（总部规定 vs 上海子公司）。
 *
 * 动机（实测）：模型此前只看到《文件名》+ 正文，不知道层级与适用范围，
 * 于是遇到两份文件给出不同数字时只能自行推断（E05 密码 90 天 vs 45/180 天），
 * 或把别的主体的规定套到问题主体上（AZ07/AZ08）。而这些信息本来就在文档头里。
 *
 * 数据源：由 {@code src/test/resources/eval/extract_metadata.py} 以确定性正则抽取，
 * 路径可用 {@code rag.context.metadata-path} 覆盖。**文件缺失或解析失败时优雅降级为不标注**
 * （返回原文），绝不让应用启动失败。
 *
 * 标签格式：{@code 【制度·北京总部·现行】《05-考勤管理制度》} —— 缺失字段整段省略；
 * 全部字段都缺失时退回纯原文（即"不标注"）。
 */
@Slf4j
@Service
public class DocMetadataService {

    private static final String SEP = "·";
    private static final String STATUS_CURRENT = "现行";
    private static final String STATUS_REPEALED = "已废止";

    @Value("${rag.context.metadata-path:src/test/resources/eval/doc-metadata.json}")
    private String metadataPath;

    /** 只读快照：启动时加载一次，之后不再变更（volatile 以便优雅降级时整体替换） */
    private volatile Map<String, DocMeta> metadata = Map.of();

    /** 单篇文档的元数据；字段缺失时为空值 */
    public record DocMeta(List<String> scope, String status, Integer year, String docType) {
    }

    @PostConstruct
    void load() {
        File file = new File(metadataPath);
        if (!file.isFile()) {
            log.warn("文档元数据文件不存在，上下文标注降级为关闭: {}", file.getAbsolutePath());
            return;
        }
        try {
            ObjectMapper mapper = new ObjectMapper();
            Map<String, Map<String, Object>> raw = mapper.readValue(file,
                    new TypeReference<Map<String, Map<String, Object>>>() { });
            Map<String, DocMeta> loaded = new java.util.HashMap<>();
            for (Map.Entry<String, Map<String, Object>> e : raw.entrySet()) {
                Map<String, Object> v = e.getValue();
                if (v == null) {
                    continue;
                }
                loaded.put(e.getKey(), new DocMeta(
                        stringList(v.get("scope")),
                        v.get("status") == null ? null : String.valueOf(v.get("status")),
                        v.get("year") instanceof Number n ? n.intValue() : null,
                        v.get("doc_type") == null ? null : String.valueOf(v.get("doc_type"))));
            }
            this.metadata = Map.copyOf(loaded);
            log.info("文档元数据加载完成: {} 篇（来源 {}）", this.metadata.size(), file.getPath());
        } catch (Exception e) {
            // 解析失败不应影响服务：降级为不标注
            log.warn("文档元数据加载失败，上下文标注降级为关闭: {} ({})",
                    file.getAbsolutePath(), e.getMessage());
            this.metadata = Map.of();
        }
    }

    public boolean isEnabled() {
        return !metadata.isEmpty();
    }

    public int size() {
        return metadata.size();
    }

    /** 只取标签部分（如 {@code 【制度·北京总部·现行】}）；无可用元数据时返回空串 */
    public String tag(String fileName) {
        if (fileName == null || metadata.isEmpty()) {
            return "";
        }
        DocMeta meta = metadata.get(fileName);
        if (meta == null) {
            return "";
        }
        List<String> parts = new ArrayList<>(3);
        if (meta.docType() != null && !meta.docType().isBlank()) {
            parts.add(meta.docType());
        }
        String scope = scopeText(meta.scope());
        if (!scope.isEmpty()) {
            parts.add(scope);
        }
        String status = statusText(meta.status());
        if (!status.isEmpty()) {
            parts.add(status);
        }
        return parts.isEmpty() ? "" : "【" + String.join(SEP, parts) + "】";
    }

    /**
     * 给一个 chunk 加元数据标签：{@code 【类型·范围·状态】《文件名》\n正文}。
     * 无元数据 / 未启用 / 文件名为空时，原样返回正文（不猜、不加空标签）。
     */
    public String label(String fileName, String content) {
        String body = content == null ? "" : content;
        String prefix = tag(fileName);
        if (prefix.isEmpty() || fileName == null || fileName.isBlank()) {
            return body;
        }
        return prefix + "《" + fileName + "》\n" + body;
    }

    /** 多个适用范围用 "/" 连接（如 北京总部/各子公司），避免与字段分隔符 · 混淆 */
    private static String scopeText(List<String> scope) {
        if (scope == null || scope.isEmpty()) {
            return "";
        }
        return String.join("/", scope);
    }

    private static String statusText(String status) {
        if (status == null) {
            return "";
        }
        return switch (status) {
            case "current" -> STATUS_CURRENT;
            case "repealed" -> STATUS_REPEALED;
            default -> "";   // 未知取值不猜
        };
    }

    private static List<String> stringList(Object value) {
        if (!(value instanceof List<?> list)) {
            return List.of();
        }
        List<String> out = new ArrayList<>(list.size());
        for (Object item : list) {
            if (item != null && !String.valueOf(item).isBlank()) {
                out.add(String.valueOf(item));
            }
        }
        return List.copyOf(out);
    }
}
