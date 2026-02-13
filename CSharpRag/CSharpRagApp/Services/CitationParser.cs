using System.Text.Json;

namespace CSharpRagApp.Services;

/// <summary>
/// Service for parsing citations from RAG responses
/// </summary>
public interface ICitationParser
{
    List<Citation> ParseCitations(string jsonResponse);
    string FormatCitation(Citation citation, int number);
    string TruncateContent(string content, int maxLength = 150);
}

/// <summary>
/// Represents a citation from a RAG response
/// </summary>
public class Citation
{
    public string? Title { get; set; }
    public string? FilePath { get; set; }
    public string? Content { get; set; }
    
    public string DisplayTitle => Title ?? FilePath ?? "Unknown Document";
}

public class CitationParser : ICitationParser
{
    public List<Citation> ParseCitations(string jsonResponse)
    {
        var citations = new List<Citation>();
        
        if (string.IsNullOrEmpty(jsonResponse))
            return citations;

        try
        {
            using var doc = JsonDocument.Parse(jsonResponse);
            
            if (!doc.RootElement.TryGetProperty("choices", out var choices) || 
                choices.GetArrayLength() == 0)
            {
                return citations;
            }

            var firstChoice = choices[0];
            if (!firstChoice.TryGetProperty("message", out var message) ||
                !message.TryGetProperty("context", out var context) ||
                !context.TryGetProperty("citations", out var citationsArray))
            {
                return citations;
            }

            foreach (var citationElement in citationsArray.EnumerateArray())
            {
                var citation = new Citation
                {
                    Title = citationElement.TryGetProperty("title", out var t) ? t.GetString() : null,
                    FilePath = citationElement.TryGetProperty("filepath", out var f) ? f.GetString() : null,
                    Content = citationElement.TryGetProperty("content", out var c) ? c.GetString() : null
                };
                citations.Add(citation);
            }
        }
        catch (JsonException)
        {
            // Return empty list on parse errors
        }

        return citations;
    }

    public string FormatCitation(Citation citation, int number)
    {
        var displayTitle = citation.Title ?? citation.FilePath ?? $"Document {number}";
        var result = $"  [{number}] {displayTitle}";

        if (!string.IsNullOrEmpty(citation.Content))
        {
            var preview = TruncateContent(citation.Content);
            result += $"\n      {preview}";
        }

        return result;
    }

    public string TruncateContent(string content, int maxLength = 150)
    {
        if (string.IsNullOrEmpty(content))
            return string.Empty;

        if (content.Length <= maxLength)
            return content;

        return content.Substring(0, maxLength) + "...";
    }
}
