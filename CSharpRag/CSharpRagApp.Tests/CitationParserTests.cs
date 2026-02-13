using CSharpRagApp.Services;
using FluentAssertions;

namespace CSharpRagApp.Tests;

public class CitationParserTests
{
    private readonly CitationParser _parser;

    public CitationParserTests()
    {
        _parser = new CitationParser();
    }

    [Fact]
    public void ParseCitations_WithValidJson_ReturnsCitations()
    {
        // Arrange
        var json = @"{
            ""choices"": [{
                ""message"": {
                    ""content"": ""Test response"",
                    ""context"": {
                        ""citations"": [
                            {
                                ""title"": ""Northwind Health Plus"",
                                ""filepath"": ""docs/health-plus.pdf"",
                                ""content"": ""Coverage details for Northwind Health Plus plan""
                            },
                            {
                                ""title"": ""Standard Plan Guide"",
                                ""filepath"": ""docs/standard.pdf"",
                                ""content"": ""Standard plan benefits and coverage""
                            }
                        ]
                    }
                }
            }]
        }";

        // Act
        var citations = _parser.ParseCitations(json);

        // Assert
        citations.Should().HaveCount(2);
        citations[0].Title.Should().Be("Northwind Health Plus");
        citations[0].FilePath.Should().Be("docs/health-plus.pdf");
        citations[0].Content.Should().Contain("Coverage details");
        citations[1].Title.Should().Be("Standard Plan Guide");
    }

    [Fact]
    public void ParseCitations_WithEmptyJson_ReturnsEmptyList()
    {
        // Act
        var citations = _parser.ParseCitations("");

        // Assert
        citations.Should().BeEmpty();
    }

    [Fact]
    public void ParseCitations_WithNullJson_ReturnsEmptyList()
    {
        // Act
        var citations = _parser.ParseCitations(null!);

        // Assert
        citations.Should().BeEmpty();
    }

    [Fact]
    public void ParseCitations_WithInvalidJson_ReturnsEmptyList()
    {
        // Act
        var citations = _parser.ParseCitations("not valid json");

        // Assert
        citations.Should().BeEmpty();
    }

    [Fact]
    public void ParseCitations_WithNoCitations_ReturnsEmptyList()
    {
        // Arrange
        var json = @"{
            ""choices"": [{
                ""message"": {
                    ""content"": ""Test response""
                }
            }]
        }";

        // Act
        var citations = _parser.ParseCitations(json);

        // Assert
        citations.Should().BeEmpty();
    }

    [Fact]
    public void ParseCitations_WithEmptyChoices_ReturnsEmptyList()
    {
        // Arrange
        var json = @"{""choices"": []}";

        // Act
        var citations = _parser.ParseCitations(json);

        // Assert
        citations.Should().BeEmpty();
    }

    [Fact]
    public void Citation_DisplayTitle_UsesTitleWhenAvailable()
    {
        // Arrange
        var citation = new Citation { Title = "My Document", FilePath = "path/doc.pdf" };

        // Assert
        citation.DisplayTitle.Should().Be("My Document");
    }

    [Fact]
    public void Citation_DisplayTitle_UsesFilePathWhenTitleIsNull()
    {
        // Arrange
        var citation = new Citation { FilePath = "path/doc.pdf" };

        // Assert
        citation.DisplayTitle.Should().Be("path/doc.pdf");
    }

    [Fact]
    public void Citation_DisplayTitle_ReturnsUnknownDocumentWhenBothNull()
    {
        // Arrange
        var citation = new Citation();

        // Assert
        citation.DisplayTitle.Should().Be("Unknown Document");
    }

    [Fact]
    public void FormatCitation_WithTitle_FormatsCorrectly()
    {
        // Arrange
        var citation = new Citation
        {
            Title = "Health Plan Guide",
            Content = "This is the content"
        };

        // Act
        var result = _parser.FormatCitation(citation, 1);

        // Assert
        result.Should().Contain("[1] Health Plan Guide");
        result.Should().Contain("This is the content");
    }

    [Fact]
    public void FormatCitation_WithoutContent_OmitsContentLine()
    {
        // Arrange
        var citation = new Citation { Title = "Health Plan Guide" };

        // Act
        var result = _parser.FormatCitation(citation, 2);

        // Assert
        result.Should().Be("  [2] Health Plan Guide");
        result.Should().NotContain("\n");
    }

    [Fact]
    public void TruncateContent_ShortContent_ReturnsUnchanged()
    {
        // Act
        var result = _parser.TruncateContent("Short content", 150);

        // Assert
        result.Should().Be("Short content");
    }

    [Fact]
    public void TruncateContent_LongContent_TruncatesWithEllipsis()
    {
        // Arrange
        var longContent = new string('x', 200);

        // Act
        var result = _parser.TruncateContent(longContent, 150);

        // Assert
        result.Should().HaveLength(153); // 150 + "..."
        result.Should().EndWith("...");
    }

    [Fact]
    public void TruncateContent_ExactLength_ReturnsUnchanged()
    {
        // Arrange
        var content = new string('x', 150);

        // Act
        var result = _parser.TruncateContent(content, 150);

        // Assert
        result.Should().HaveLength(150);
        result.Should().NotEndWith("...");
    }

    [Fact]
    public void TruncateContent_EmptyString_ReturnsEmpty()
    {
        // Act
        var result = _parser.TruncateContent("");

        // Assert
        result.Should().BeEmpty();
    }

    [Fact]
    public void TruncateContent_NullString_ReturnsEmpty()
    {
        // Act
        var result = _parser.TruncateContent(null!);

        // Assert
        result.Should().BeEmpty();
    }

    [Fact]
    public void TruncateContent_CustomMaxLength_UsesCustomLength()
    {
        // Arrange
        var content = "This is a test string that should be truncated";

        // Act
        var result = _parser.TruncateContent(content, 10);

        // Assert
        result.Should().Be("This is a ...");
    }
}
