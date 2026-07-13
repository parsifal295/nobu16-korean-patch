using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace N16KrFileOnly
{
    public static class JsonKeyGuard
    {
        public static void AssertFile(string path)
        {
            AssertNoDuplicateKeys(File.ReadAllBytes(path));
        }

        public static void AssertNoDuplicateKeys(byte[] utf8)
        {
            if (utf8 == null)
                throw new ArgumentNullException("utf8");
            if (utf8.Length >= 3 && utf8[0] == 0xEF && utf8[1] == 0xBB && utf8[2] == 0xBF)
                throw new InvalidDataException("JSON UTF-8 BOM is forbidden");
            string text;
            try
            {
                text = new UTF8Encoding(false, true).GetString(utf8);
            }
            catch (DecoderFallbackException exception)
            {
                throw new InvalidDataException("JSON is not strict UTF-8", exception);
            }
            new Parser(text).ParseDocument();
        }

        private sealed class Parser
        {
            private readonly string text;
            private int position;
            private int depth;

            internal Parser(string value)
            {
                text = value;
            }

            internal void ParseDocument()
            {
                SkipWhitespace();
                ParseValue();
                SkipWhitespace();
                if (position != text.Length)
                    Fail("trailing content");
            }

            private void ParseValue()
            {
                SkipWhitespace();
                if (position >= text.Length)
                    Fail("missing value");
                char current = text[position];
                if (current == '{') ParseObject();
                else if (current == '[') ParseArray();
                else if (current == '"') ParseString();
                else if (current == 't') ParseLiteral("true");
                else if (current == 'f') ParseLiteral("false");
                else if (current == 'n') ParseLiteral("null");
                else if (current == '-' || (current >= '0' && current <= '9')) ParseNumber();
                else Fail("invalid value");
            }

            private void EnterContainer()
            {
                depth++;
                if (depth > 128)
                    Fail("maximum JSON depth exceeded");
            }

            private void LeaveContainer()
            {
                depth--;
            }

            private void ParseObject()
            {
                EnterContainer();
                position++;
                SkipWhitespace();
                if (Consume('}'))
                {
                    LeaveContainer();
                    return;
                }
                HashSet<string> exact = new HashSet<string>(StringComparer.Ordinal);
                HashSet<string> folded = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                while (true)
                {
                    SkipWhitespace();
                    if (position >= text.Length || text[position] != '"')
                        Fail("object key must be a string");
                    string key = ParseString();
                    if (!exact.Add(key))
                        Fail("duplicate object key: " + key);
                    if (!folded.Add(key))
                        Fail("case-colliding object key: " + key);
                    SkipWhitespace();
                    Require(':');
                    ParseValue();
                    SkipWhitespace();
                    if (Consume('}'))
                        break;
                    Require(',');
                }
                LeaveContainer();
            }

            private void ParseArray()
            {
                EnterContainer();
                position++;
                SkipWhitespace();
                if (Consume(']'))
                {
                    LeaveContainer();
                    return;
                }
                while (true)
                {
                    ParseValue();
                    SkipWhitespace();
                    if (Consume(']'))
                        break;
                    Require(',');
                }
                LeaveContainer();
            }

            private string ParseString()
            {
                Require('"');
                StringBuilder result = new StringBuilder();
                while (position < text.Length)
                {
                    char current = text[position++];
                    if (current == '"')
                        return result.ToString();
                    if (current < 0x20)
                        Fail("control character in string");
                    if (current == '\\')
                    {
                        if (position >= text.Length)
                            Fail("incomplete string escape");
                        char escaped = text[position++];
                        if (escaped == '"' || escaped == '\\' || escaped == '/') result.Append(escaped);
                        else if (escaped == 'b') result.Append('\b');
                        else if (escaped == 'f') result.Append('\f');
                        else if (escaped == 'n') result.Append('\n');
                        else if (escaped == 'r') result.Append('\r');
                        else if (escaped == 't') result.Append('\t');
                        else if (escaped == 'u') AppendEscapedUnicode(result);
                        else Fail("invalid string escape");
                        continue;
                    }
                    if (Char.IsHighSurrogate(current))
                    {
                        if (position >= text.Length || !Char.IsLowSurrogate(text[position]))
                            Fail("unpaired high surrogate");
                        result.Append(current);
                        result.Append(text[position++]);
                    }
                    else if (Char.IsLowSurrogate(current))
                    {
                        Fail("unpaired low surrogate");
                    }
                    else
                    {
                        result.Append(current);
                    }
                }
                Fail("unterminated string");
                return null;
            }

            private void AppendEscapedUnicode(StringBuilder result)
            {
                char first = (char)ReadHex4();
                if (Char.IsHighSurrogate(first))
                {
                    if (position + 6 > text.Length || text[position] != '\\' || text[position + 1] != 'u')
                        Fail("escaped high surrogate lacks a low surrogate");
                    position += 2;
                    char second = (char)ReadHex4();
                    if (!Char.IsLowSurrogate(second))
                        Fail("escaped surrogate pair is invalid");
                    result.Append(first);
                    result.Append(second);
                }
                else if (Char.IsLowSurrogate(first))
                {
                    Fail("escaped low surrogate lacks a high surrogate");
                }
                else
                {
                    result.Append(first);
                }
            }

            private int ReadHex4()
            {
                if (position + 4 > text.Length)
                    Fail("incomplete Unicode escape");
                int value = 0;
                for (int index = 0; index < 4; index++)
                {
                    char current = text[position++];
                    int digit;
                    if (current >= '0' && current <= '9') digit = current - '0';
                    else if (current >= 'a' && current <= 'f') digit = current - 'a' + 10;
                    else if (current >= 'A' && current <= 'F') digit = current - 'A' + 10;
                    else
                    {
                        Fail("invalid Unicode escape");
                        return 0;
                    }
                    value = (value << 4) | digit;
                }
                return value;
            }

            private void ParseNumber()
            {
                if (Consume('-') && position >= text.Length)
                    Fail("incomplete number");
                if (Consume('0'))
                {
                    if (position < text.Length && Char.IsDigit(text[position]))
                        Fail("leading zero in number");
                }
                else
                {
                    RequireDigitOneToNine();
                    while (position < text.Length && Char.IsDigit(text[position])) position++;
                }
                if (Consume('.'))
                {
                    RequireDigit();
                    while (position < text.Length && Char.IsDigit(text[position])) position++;
                }
                if (position < text.Length && (text[position] == 'e' || text[position] == 'E'))
                {
                    position++;
                    if (position < text.Length && (text[position] == '+' || text[position] == '-')) position++;
                    RequireDigit();
                    while (position < text.Length && Char.IsDigit(text[position])) position++;
                }
            }

            private void RequireDigitOneToNine()
            {
                if (position >= text.Length || text[position] < '1' || text[position] > '9')
                    Fail("number requires a nonzero digit");
                position++;
            }

            private void RequireDigit()
            {
                if (position >= text.Length || !Char.IsDigit(text[position]))
                    Fail("number requires a digit");
                position++;
            }

            private void ParseLiteral(string literal)
            {
                if (position + literal.Length > text.Length ||
                    !String.Equals(text.Substring(position, literal.Length), literal, StringComparison.Ordinal))
                    Fail("invalid literal");
                position += literal.Length;
            }

            private void SkipWhitespace()
            {
                while (position < text.Length)
                {
                    char current = text[position];
                    if (current != ' ' && current != '\t' && current != '\r' && current != '\n')
                        break;
                    position++;
                }
            }

            private bool Consume(char expected)
            {
                if (position < text.Length && text[position] == expected)
                {
                    position++;
                    return true;
                }
                return false;
            }

            private void Require(char expected)
            {
                if (!Consume(expected))
                    Fail("expected '" + expected + "'");
            }

            private void Fail(string message)
            {
                throw new InvalidDataException("Invalid JSON at character " + position + ": " + message);
            }
        }
    }
}
