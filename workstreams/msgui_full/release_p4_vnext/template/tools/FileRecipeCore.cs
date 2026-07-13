using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace N16KrFileOnly
{
    public static class FileRecipeCore
    {
        private const int WrapperSize = 24;
        private const int LinkHeaderSize = 16;

        private sealed class LinkEntry
        {
            public int Index;
            public long Offset;
            public int StoredSize;
            public byte[] Data = Array.Empty<byte>();
            public byte[] Gap = Array.Empty<byte>();
            public bool VirtualEmpty;
        }

        private sealed class LinkArchive
        {
            public byte[] FixedHeader = Array.Empty<byte>();
            public byte[] PreDataPadding = Array.Empty<byte>();
            public int OriginalSize;
            public List<LinkEntry> Entries = new List<LinkEntry>();
        }

        private sealed class G1nLayout
        {
            public int HeaderSize;
            public int AtlasOffset;
            public int PaletteCount;
            public int[] TableOffsets = Array.Empty<int>();
            public int[] TableEnds = Array.Empty<int>();
        }

        private static ushort U16(byte[] data, int offset)
        {
            RequireRange(data, offset, 2, "u16");
            return (ushort)(data[offset] | (data[offset + 1] << 8));
        }

        private static uint U32(byte[] data, int offset)
        {
            RequireRange(data, offset, 4, "u32");
            return (uint)(data[offset] | (data[offset + 1] << 8) |
                (data[offset + 2] << 16) | (data[offset + 3] << 24));
        }

        private static ulong U64(byte[] data, int offset)
        {
            RequireRange(data, offset, 8, "u64");
            return (ulong)U32(data, offset) | ((ulong)U32(data, offset + 4) << 32);
        }

        private static void PutU16(byte[] data, int offset, int value)
        {
            RequireRange(data, offset, 2, "u16 write");
            if (value < 0 || value > ushort.MaxValue)
                throw new InvalidDataException("u16 value is outside range");
            data[offset] = (byte)value;
            data[offset + 1] = (byte)(value >> 8);
        }

        private static void PutU32(byte[] data, int offset, long value)
        {
            RequireRange(data, offset, 4, "u32 write");
            if (value < 0 || value > uint.MaxValue)
                throw new InvalidDataException("u32 value is outside range");
            data[offset] = (byte)value;
            data[offset + 1] = (byte)(value >> 8);
            data[offset + 2] = (byte)(value >> 16);
            data[offset + 3] = (byte)(value >> 24);
        }

        private static void PutU64(byte[] data, int offset, long value)
        {
            RequireRange(data, offset, 8, "u64 write");
            if (value < 0)
                throw new InvalidDataException("u64 value is negative");
            PutU32(data, offset, (uint)value);
            PutU32(data, offset + 4, (uint)((ulong)value >> 32));
        }

        private static void RequireRange(byte[] data, int offset, int length, string label)
        {
            if (offset < 0 || length < 0 || (long)offset + length > data.Length)
                throw new InvalidDataException(label + " is outside the byte array");
        }

        private static byte[] Slice(byte[] data, int offset, int length)
        {
            RequireRange(data, offset, length, "slice");
            byte[] result = new byte[length];
            Buffer.BlockCopy(data, offset, result, 0, length);
            return result;
        }

        public static string Sha256(byte[] data)
        {
            using (SHA256 digest = SHA256.Create())
                return BitConverter.ToString(digest.ComputeHash(data)).Replace("-", "");
        }

        public static string Sha256File(string path)
        {
            using (FileStream stream = File.OpenRead(path))
            using (SHA256 digest = SHA256.Create())
                return BitConverter.ToString(digest.ComputeHash(stream)).Replace("-", "");
        }

        public static void WriteDurable(string path, byte[] data)
        {
            using (FileStream stream = new FileStream(
                path, FileMode.CreateNew, FileAccess.Write, FileShare.None, 1024 * 1024,
                FileOptions.SequentialScan))
            {
                stream.Write(data, 0, data.Length);
                stream.Flush(true);
            }
        }

        public static void CopyDurable(string source, string destination)
        {
            using (FileStream input = new FileStream(
                source, FileMode.Open, FileAccess.Read, FileShare.Read, 1024 * 1024,
                FileOptions.SequentialScan))
            using (FileStream output = new FileStream(
                destination, FileMode.CreateNew, FileAccess.Write, FileShare.None, 1024 * 1024,
                FileOptions.SequentialScan))
            {
                input.CopyTo(output, 1024 * 1024);
                output.Flush(true);
            }
        }

        private static byte[] RawLz4Decompress(byte[] source, int expectedSize)
        {
            if (expectedSize < 0)
                throw new InvalidDataException("negative decompressed size");
            byte[] output = new byte[expectedSize];
            int sourcePos = 0;
            int outputPos = 0;
            while (sourcePos < source.Length)
            {
                int token = source[sourcePos++];
                int literalLength = token >> 4;
                if (literalLength == 15)
                {
                    int extension;
                    do
                    {
                        if (sourcePos >= source.Length)
                            throw new InvalidDataException("truncated LZ4 literal length");
                        extension = source[sourcePos++];
                        literalLength += extension;
                    }
                    while (extension == 255);
                }
                if ((long)sourcePos + literalLength > source.Length ||
                    (long)outputPos + literalLength > output.Length)
                    throw new InvalidDataException("invalid LZ4 literal run");
                Buffer.BlockCopy(source, sourcePos, output, outputPos, literalLength);
                sourcePos += literalLength;
                outputPos += literalLength;
                if (sourcePos == source.Length)
                    break;
                if (sourcePos + 2 > source.Length)
                    throw new InvalidDataException("truncated LZ4 match offset");
                int matchOffset = source[sourcePos] | (source[sourcePos + 1] << 8);
                sourcePos += 2;
                if (matchOffset <= 0 || matchOffset > outputPos)
                    throw new InvalidDataException("invalid LZ4 match offset");
                int matchLength = (token & 15) + 4;
                if ((token & 15) == 15)
                {
                    int extension;
                    do
                    {
                        if (sourcePos >= source.Length)
                            throw new InvalidDataException("truncated LZ4 match length");
                        extension = source[sourcePos++];
                        matchLength += extension;
                    }
                    while (extension == 255);
                }
                if ((long)outputPos + matchLength > output.Length)
                    throw new InvalidDataException("LZ4 match exceeds expected output");
                int matchPos = outputPos - matchOffset;
                for (int index = 0; index < matchLength; index++)
                    output[outputPos++] = output[matchPos + index];
            }
            if (sourcePos != source.Length || outputPos != output.Length)
                throw new InvalidDataException("LZ4 decoded size mismatch");
            return output;
        }

        private static byte[] RawLz4Literal(byte[] raw)
        {
            if (raw.Length == 0)
                return Array.Empty<byte>();
            using (MemoryStream output = new MemoryStream(raw.Length + raw.Length / 255 + 16))
            {
                if (raw.Length < 15)
                {
                    output.WriteByte((byte)(raw.Length << 4));
                }
                else
                {
                    output.WriteByte(0xF0);
                    int remaining = raw.Length - 15;
                    while (remaining >= 255)
                    {
                        output.WriteByte(255);
                        remaining -= 255;
                    }
                    output.WriteByte((byte)remaining);
                }
                output.Write(raw, 0, raw.Length);
                return output.ToArray();
            }
        }

        public static byte[] DecompressWrapper(byte[] wrapper)
        {
            if (wrapper.Length < WrapperSize)
                throw new InvalidDataException("LZ4 wrapper is too small");
            ulong rawSize64 = U64(wrapper, 8);
            ulong compressedSize64 = U64(wrapper, 16);
            if (rawSize64 > int.MaxValue || compressedSize64 > int.MaxValue)
                throw new InvalidDataException("LZ4 wrapper exceeds supported size");
            int compressedSize = (int)compressedSize64;
            if (compressedSize != wrapper.Length - WrapperSize)
                throw new InvalidDataException("LZ4 wrapper compressed size mismatch");
            return RawLz4Decompress(
                Slice(wrapper, WrapperSize, compressedSize), (int)rawSize64);
        }

        public static byte[] RecompressWrapper(byte[] raw, byte[] template)
        {
            if (template.Length < WrapperSize)
                throw new InvalidDataException("template wrapper is too small");
            byte[] compressed = RawLz4Literal(raw);
            byte[] output = new byte[WrapperSize + compressed.Length];
            Buffer.BlockCopy(template, 0, output, 0, 8);
            PutU64(output, 8, raw.Length);
            PutU64(output, 16, compressed.Length);
            Buffer.BlockCopy(compressed, 0, output, WrapperSize, compressed.Length);
            return output;
        }

        private static LinkArchive ParseLink(byte[] blob)
        {
            if (blob.Length < LinkHeaderSize || Encoding.ASCII.GetString(blob, 0, 4) != "LINK")
                throw new InvalidDataException("not a LINK archive");
            int count = checked((int)U32(blob, 4));
            int tableEnd = checked(LinkHeaderSize + count * 8);
            if (tableEnd > blob.Length)
                throw new InvalidDataException("LINK table exceeds file size");
            long[] offsets = new long[count];
            int[] sizes = new int[count];
            for (int index = 0; index < count; index++)
            {
                offsets[index] = U32(blob, LinkHeaderSize + index * 8);
                uint size = U32(blob, LinkHeaderSize + index * 8 + 4);
                if (size > int.MaxValue)
                    throw new InvalidDataException("LINK entry is too large");
                sizes[index] = (int)size;
            }
            LinkArchive archive = new LinkArchive
            {
                FixedHeader = Slice(blob, 0, LinkHeaderSize),
                OriginalSize = blob.Length
            };
            if (count == 0)
            {
                archive.PreDataPadding = Slice(blob, LinkHeaderSize, blob.Length - LinkHeaderSize);
                return archive;
            }
            if (offsets[0] < tableEnd || offsets[0] > blob.Length)
                throw new InvalidDataException("invalid first LINK entry offset");
            archive.PreDataPadding = Slice(blob, tableEnd, (int)offsets[0] - tableEnd);
            long previous = -1;
            for (int index = 0; index < count; index++)
            {
                long offset = offsets[index];
                int size = sizes[index];
                long next = index + 1 < count ? offsets[index + 1] : blob.Length;
                if (offset < previous)
                    throw new InvalidDataException("LINK offsets are not monotonic");
                bool virtualEmpty = offset >= blob.Length && size == 0;
                if (virtualEmpty)
                {
                    for (int rest = index; rest < count; rest++)
                        if (sizes[rest] != 0)
                            throw new InvalidDataException("invalid virtual LINK entry");
                    archive.Entries.Add(new LinkEntry
                    {
                        Index = index,
                        Offset = offset,
                        StoredSize = 0,
                        VirtualEmpty = true
                    });
                    previous = offset;
                    continue;
                }
                long end = offset + size;
                if (offset > blob.Length || end > blob.Length || end > next)
                    throw new InvalidDataException("LINK entry range is invalid");
                int physicalNext = (int)Math.Min(next, blob.Length);
                archive.Entries.Add(new LinkEntry
                {
                    Index = index,
                    Offset = offset,
                    StoredSize = size,
                    Data = Slice(blob, (int)offset, size),
                    Gap = Slice(blob, (int)end, physicalNext - (int)end),
                    VirtualEmpty = false
                });
                previous = offset;
            }
            return archive;
        }

        public static byte[] ExtractLinkEntryRaw(byte[] archiveBytes, int entryIndex)
        {
            LinkArchive archive = ParseLink(archiveBytes);
            if (entryIndex < 0 || entryIndex >= archive.Entries.Count ||
                archive.Entries[entryIndex].VirtualEmpty)
                throw new InvalidDataException("requested LINK entry is unavailable");
            return DecompressWrapper(archive.Entries[entryIndex].Data);
        }

        public static byte[] ReplaceLinkRawEntries(
            byte[] archiveBytes, int[] entryIndices, byte[][] replacementRaw)
        {
            if (entryIndices == null || replacementRaw == null ||
                entryIndices.Length != replacementRaw.Length)
                throw new ArgumentException("replacement arrays differ in length");
            LinkArchive archive = ParseLink(archiveBytes);
            Dictionary<int, byte[]> replacements = new Dictionary<int, byte[]>();
            for (int index = 0; index < entryIndices.Length; index++)
            {
                int entry = entryIndices[index];
                if (entry < 0 || entry >= archive.Entries.Count || archive.Entries[entry].VirtualEmpty)
                    throw new InvalidDataException("replacement LINK entry is unavailable");
                if (replacements.ContainsKey(entry))
                    throw new InvalidDataException("duplicate LINK replacement entry");
                replacements[entry] = RecompressWrapper(
                    replacementRaw[index], archive.Entries[entry].Data);
            }

            using (MemoryStream output = new MemoryStream())
            {
                output.Write(archive.FixedHeader, 0, archive.FixedHeader.Length);
                output.Write(new byte[archive.Entries.Count * 8], 0, archive.Entries.Count * 8);
                output.Write(archive.PreDataPadding, 0, archive.PreDataPadding.Length);
                long[] offsets = new long[archive.Entries.Count];
                int[] sizes = new int[archive.Entries.Count];
                foreach (LinkEntry entry in archive.Entries)
                {
                    if (entry.VirtualEmpty)
                    {
                        offsets[entry.Index] = output.Length + (entry.Offset - archive.OriginalSize);
                        sizes[entry.Index] = 0;
                        continue;
                    }
                    byte[] data = replacements.ContainsKey(entry.Index)
                        ? replacements[entry.Index] : entry.Data;
                    offsets[entry.Index] = output.Length;
                    sizes[entry.Index] = data.Length;
                    output.Write(data, 0, data.Length);
                    output.Write(entry.Gap, 0, entry.Gap.Length);
                }
                if (output.Length > int.MaxValue)
                    throw new InvalidDataException("rebuilt LINK archive is too large");
                byte[] result = output.ToArray();
                for (int index = 0; index < offsets.Length; index++)
                {
                    PutU32(result, LinkHeaderSize + index * 8, offsets[index]);
                    PutU32(result, LinkHeaderSize + index * 8 + 4, sizes[index]);
                }
                return result;
            }
        }

        private static G1nLayout ParseG1n(byte[] data)
        {
            if (data.Length < 0x28 || Encoding.ASCII.GetString(data, 0, 8) != "_N1G0000")
                throw new InvalidDataException("not a G1N file");
            if (U32(data, 8) != data.Length)
                throw new InvalidDataException("G1N declared size mismatch");
            int headerSize = checked((int)U32(data, 0x0C));
            int atlasOffset = checked((int)U32(data, 0x14));
            int paletteCount = checked((int)U32(data, 0x18));
            int tableCount = checked((int)U32(data, 0x1C));
            if (tableCount != 2 || headerSize != 0x20 + 4 * tableCount + 0x40 * paletteCount)
                throw new InvalidDataException("unexpected G1N header shape");
            int[] tableOffsets = {
                checked((int)U32(data, 0x20)), checked((int)U32(data, 0x24))
            };
            if (tableOffsets[0] != headerSize || tableOffsets[0] >= tableOffsets[1] ||
                tableOffsets[1] >= atlasOffset || atlasOffset > data.Length)
                throw new InvalidDataException("invalid G1N table order");
            int[] tableEnds = { tableOffsets[1], atlasOffset };
            for (int table = 0; table < 2; table++)
            {
                int recordBytes = tableEnds[table] - tableOffsets[table] - 0x20000;
                if (recordBytes < 0 || recordBytes % 12 != 0)
                    throw new InvalidDataException("malformed G1N record region");
            }
            return new G1nLayout
            {
                HeaderSize = headerSize,
                AtlasOffset = atlasOffset,
                PaletteCount = paletteCount,
                TableOffsets = tableOffsets,
                TableEnds = tableEnds
            };
        }

        public static byte[] BuildG1n(
            byte[] stock, int targetSize, int targetAtlasOffset, int[] targetTableOffsets,
            int[] codepointsTable0, int[] ordinalsTable0,
            int[] codepointsTable1, int[] ordinalsTable1,
            byte[] appendedTable0, byte[] appendedTable1, byte[] pixelPayload)
        {
            if (targetTableOffsets == null || targetTableOffsets.Length != 2 ||
                codepointsTable0 == null || ordinalsTable0 == null ||
                codepointsTable1 == null || ordinalsTable1 == null ||
                codepointsTable0.Length != ordinalsTable0.Length ||
                codepointsTable1.Length != ordinalsTable1.Length ||
                appendedTable0 == null || appendedTable1 == null || pixelPayload == null ||
                appendedTable0.Length != checked(codepointsTable0.Length * 12) ||
                appendedTable1.Length != checked(codepointsTable1.Length * 12))
                throw new ArgumentException("invalid G1N recipe arrays");
            G1nLayout layout = ParseG1n(stock);
            if (targetTableOffsets[0] != layout.TableOffsets[0] ||
                targetTableOffsets[1] != layout.TableOffsets[1] + appendedTable0.Length ||
                targetAtlasOffset != layout.AtlasOffset + appendedTable0.Length + appendedTable1.Length ||
                targetSize != stock.Length + appendedTable0.Length + appendedTable1.Length + pixelPayload.Length)
                throw new InvalidDataException("G1N recipe structural offsets do not match stock");

            byte[] output = new byte[targetSize];
            Buffer.BlockCopy(stock, 0, output, 0, layout.HeaderSize);
            PutU32(output, 8, targetSize);
            PutU32(output, 0x14, targetAtlasOffset);
            PutU32(output, 0x20, targetTableOffsets[0]);
            PutU32(output, 0x24, targetTableOffsets[1]);

            byte[][] appended = { appendedTable0, appendedTable1 };
            int[][] codepoints = { codepointsTable0, codepointsTable1 };
            int[][] ordinals = { ordinalsTable0, ordinalsTable1 };
            for (int table = 0; table < 2; table++)
            {
                int sourceOffset = layout.TableOffsets[table];
                int destinationOffset = targetTableOffsets[table];
                Buffer.BlockCopy(stock, sourceOffset, output, destinationOffset, 0x20000);
                for (int index = 0; index < codepoints[table].Length; index++)
                {
                    int codepoint = codepoints[table][index];
                    if (codepoint < 0 || codepoint > 0xFFFF ||
                        (index > 0 && codepoint <= codepoints[table][index - 1]))
                        throw new InvalidDataException("codepoint list is outside BMP or not sorted/unique");
                    if (ordinals[table][index] < 0 || ordinals[table][index] > 0xFFFF)
                        throw new InvalidDataException("ordinal is outside the G1N map range");
                    int mapOffset = destinationOffset + codepoint * 2;
                    if (U16(output, mapOffset) != 0)
                        throw new InvalidDataException("stock G1N codepoint ordinal is not zero");
                    PutU16(output, mapOffset, ordinals[table][index]);
                }
                int oldRecordsStart = sourceOffset + 0x20000;
                int oldRecordsLength = layout.TableEnds[table] - oldRecordsStart;
                int destinationRecordsStart = destinationOffset + 0x20000;
                Buffer.BlockCopy(stock, oldRecordsStart, output, destinationRecordsStart, oldRecordsLength);
                Buffer.BlockCopy(
                    appended[table], 0, output, destinationRecordsStart + oldRecordsLength,
                    appended[table].Length);
            }
            int stockAtlasLength = stock.Length - layout.AtlasOffset;
            Buffer.BlockCopy(stock, layout.AtlasOffset, output, targetAtlasOffset, stockAtlasLength);
            Buffer.BlockCopy(pixelPayload, 0, output, targetAtlasOffset + stockAtlasLength, pixelPayload.Length);
            ParseG1n(output);
            return output;
        }

        private static byte[] HashUtf16(string value)
        {
            using (SHA256 digest = SHA256.Create())
                return digest.ComputeHash(Encoding.Unicode.GetBytes(value));
        }

        private static string Hex(byte[] value)
        {
            return BitConverter.ToString(value).Replace("-", "");
        }

        public static byte[] ApplyMessageRecipe(
            byte[] stockWrapper, int expectedCount, int[] ids,
            string[] expectedSourceHashes, string[] replacements)
        {
            if (ids == null || expectedSourceHashes == null || replacements == null ||
                ids.Length != expectedSourceHashes.Length || ids.Length != replacements.Length)
                throw new ArgumentException("invalid message recipe arrays");
            byte[] raw = DecompressWrapper(stockWrapper);
            if (raw.Length < 0x24 || U32(raw, 0) != 1)
                throw new InvalidDataException("unsupported message table");
            int blockOffset = checked((int)U32(raw, 4));
            int logicalSize = checked((int)U32(raw, 8));
            int logicalEnd = checked(blockOffset + logicalSize);
            if (blockOffset < 0x0C || logicalEnd > raw.Length || raw.Length - logicalEnd >= 4)
                throw new InvalidDataException("invalid message logical range");
            for (int offset = logicalEnd; offset < raw.Length; offset++)
                if (raw[offset] != 0)
                    throw new InvalidDataException("invalid message alignment padding");
            int tableOffset = checked(blockOffset + (int)U32(raw, blockOffset + 0x0C));
            int firstOffset = checked((int)U32(raw, tableOffset));
            if (firstOffset < 4 || firstOffset % 4 != 0)
                throw new InvalidDataException("invalid message offset table");
            int count = firstOffset / 4;
            if (count != expectedCount)
                throw new InvalidDataException("message string count mismatch");
            int[] offsets = new int[count];
            string[] texts = new string[count];
            int[] ends = new int[count];
            for (int index = 0; index < count; index++)
            {
                offsets[index] = checked((int)U32(raw, tableOffset + index * 4));
                if (index > 0 && offsets[index] <= offsets[index - 1])
                    throw new InvalidDataException("message offsets are not increasing");
                int start = checked(tableOffset + offsets[index]);
                if ((start & 1) != 0 || start < 0 || start >= logicalEnd)
                    throw new InvalidDataException("invalid message string start");
                int end = start;
                while (end + 1 < logicalEnd && (raw[end] != 0 || raw[end + 1] != 0))
                    end += 2;
                if (end + 1 >= logicalEnd)
                    throw new InvalidDataException("unterminated message string");
                texts[index] = Encoding.Unicode.GetString(raw, start, end - start);
                ends[index] = end + 2;
            }
            for (int index = 0; index + 1 < count; index++)
                if (ends[index] != tableOffset + offsets[index + 1])
                    throw new InvalidDataException("message string pool is not contiguous");
            if (ends[count - 1] != logicalEnd)
                throw new InvalidDataException("message string pool end mismatch");

            HashSet<int> seen = new HashSet<int>();
            for (int operation = 0; operation < ids.Length; operation++)
            {
                int id = ids[operation];
                if (id < 0 || id >= count || !seen.Add(id))
                    throw new InvalidDataException("invalid or duplicate message id");
                string actualHash = Hex(HashUtf16(texts[id]));
                if (!String.Equals(actualHash, expectedSourceHashes[operation], StringComparison.OrdinalIgnoreCase))
                    throw new InvalidDataException("message source hash mismatch at id " + id);
                if (String.IsNullOrEmpty(replacements[operation]) || replacements[operation].IndexOf('\0') >= 0)
                    throw new InvalidDataException("invalid message replacement at id " + id);
                texts[id] = replacements[operation];
            }

            int stringStart = checked(tableOffset + firstOffset);
            byte[] prefix = Slice(raw, 0, stringStart);
            using (MemoryStream pool = new MemoryStream())
            {
                int relative = firstOffset;
                for (int index = 0; index < count; index++)
                {
                    PutU32(prefix, tableOffset + index * 4, relative);
                    byte[] encoded = Encoding.Unicode.GetBytes(texts[index]);
                    pool.Write(encoded, 0, encoded.Length);
                    pool.WriteByte(0);
                    pool.WriteByte(0);
                    relative = checked(relative + encoded.Length + 2);
                }
                int unpaddedSize = checked(prefix.Length + (int)pool.Length);
                int padding = (4 - (unpaddedSize & 3)) & 3;
                byte[] rebuiltRaw = new byte[unpaddedSize + padding];
                Buffer.BlockCopy(prefix, 0, rebuiltRaw, 0, prefix.Length);
                byte[] poolBytes = pool.ToArray();
                Buffer.BlockCopy(poolBytes, 0, rebuiltRaw, prefix.Length, poolBytes.Length);
                PutU32(rebuiltRaw, 8, unpaddedSize - blockOffset);
                return RecompressWrapper(rebuiltRaw, stockWrapper);
            }
        }
    }
}
