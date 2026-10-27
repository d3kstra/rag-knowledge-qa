package io.github.d3kstra.rag_knowledge_qa.service;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.test.util.ReflectionTestUtils;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * 文档元数据标注单测：标签格式、字段缺失省略、未知文档不改写、文件缺失/格式错误时优雅降级。
 * 背景：模型此前只看到《文件名》+ 正文，无法裁决上下位文件冲突与主体错配（E05/AZ07/AZ08）。
 */
class DocMetadataServiceTest {

    private static DocMetadataService serviceWith(Path metadataPath) {
        DocMetadataService service = new DocMetadataService();
        ReflectionTestUtils.setField(service, "metadataPath", metadataPath.toString());
        service.load();
        return service;
    }

    private static final String JSON = """
            {
              "05-考勤管理制度": {"scope": ["北京总部"], "status": "current", "year": 2026, "doc_type": "制度"},
              "F02-信息安全操作细则": {"scope": ["北京总部"], "status": "current", "year": 2026, "doc_type": "细则"},
              "N00-2026年新增办公设备配发通知": {"scope": ["北京总部", "各子公司"], "status": "current", "year": 2026, "doc_type": "通知"},
              "B01-2024年考勤管理制度": {"scope": [], "status": "repealed", "year": 2024, "doc_type": "制度"}
            }
            """;

    @Test
    @DisplayName("完整元数据：标签为【类型·范围·现行】《文件名》+ 正文")
    void labelsFullMetadata(@TempDir Path dir) throws Exception {
        Path file = dir.resolve("meta.json");
        Files.writeString(file, JSON);
        DocMetadataService service = serviceWith(file);

        assertThat(service.isEnabled()).isTrue();
        assertThat(service.label("05-考勤管理制度", "正文内容"))
                .isEqualTo("【制度·北京总部·现行】《05-考勤管理制度》\n正文内容");
    }

    @Test
    @DisplayName("多个适用范围用 / 连接，避免与字段分隔符混淆")
    void joinsMultipleScopes(@TempDir Path dir) throws Exception {
        Path file = dir.resolve("meta.json");
        Files.writeString(file, JSON);
        DocMetadataService service = serviceWith(file);

        assertThat(service.tag("N00-2026年新增办公设备配发通知"))
                .isEqualTo("【通知·北京总部/各子公司·现行】");
    }

    @Test
    @DisplayName("scope 缺失时整段省略；已废止映射为「已废止」")
    void omitsMissingFieldsAndMapsRepealed(@TempDir Path dir) throws Exception {
        Path file = dir.resolve("meta.json");
        Files.writeString(file, JSON);
        DocMetadataService service = serviceWith(file);

        assertThat(service.tag("B01-2024年考勤管理制度")).isEqualTo("【制度·已废止】");
    }

    @Test
    @DisplayName("未知文档：不猜、不加空标签，正文原样返回")
    void unknownDocumentIsUntouched(@TempDir Path dir) throws Exception {
        Path file = dir.resolve("meta.json");
        Files.writeString(file, JSON);
        DocMetadataService service = serviceWith(file);

        assertThat(service.tag("99-不存在的文档")).isEmpty();
        assertThat(service.label("99-不存在的文档", "原文")).isEqualTo("原文");
    }

    @Test
    @DisplayName("元数据文件缺失：降级为不标注（服务仍可用）")
    void missingFileDegradesGracefully(@TempDir Path dir) {
        DocMetadataService service = serviceWith(dir.resolve("not-exists.json"));

        assertThat(service.isEnabled()).isFalse();
        assertThat(service.size()).isZero();
        assertThat(service.label("05-考勤管理制度", "原文")).isEqualTo("原文");
    }

    @Test
    @DisplayName("元数据文件格式错误：降级为不标注，不抛异常")
    void malformedJsonDegradesGracefully(@TempDir Path dir) throws Exception {
        Path file = dir.resolve("broken.json");
        Files.writeString(file, "{not-json");
        DocMetadataService service = serviceWith(file);

        assertThat(service.isEnabled()).isFalse();
        assertThat(service.label("05-考勤管理制度", "原文")).isEqualTo("原文");
    }
}
