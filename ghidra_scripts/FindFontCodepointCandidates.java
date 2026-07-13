// Locate font-system string xrefs and likely Unicode/codepoint gates.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.block.BasicBlockModel;
import ghidra.program.model.data.DataType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;

import java.io.File;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class FindFontCodepointCandidates extends GhidraScript {
    private static final Set<Long> CONSTANTS = new HashSet<>(Arrays.asList(
        0x7fL, 0x80L, 0xffL, 0x100L, 0x7fffL, 0x8000L, 0xffffL,
        0x10000L, 0xd7L, 0xd7ffL, 0xd800L, 0xdfffL, 0xe000L, 0xac00L
    ));

    private PrintWriter out;

    private void line(String s) {
        println(s);
        out.println(s);
    }

    private String functionAt(Address a) {
        Function f = currentProgram.getFunctionManager().getFunctionContaining(a);
        return f == null ? "<no-function>" : f.getName() + "@" + f.getEntryPoint();
    }

    private boolean interestingString(String s) {
        String u = s.toUpperCase();
        return u.contains("FONT") || u.contains("TEXT_DRAW") ||
               u.contains("RES_LANG") || u.contains("GLYPH") || u.contains("N1G");
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        File output = new File(args.length > 0 ? args[0] : "font_codepoint_candidates.txt");
        output.getParentFile().mkdirs();
        out = new PrintWriter(output, "UTF-8");
        try {
            line("program=" + currentProgram.getName());
            line("image_base=" + currentProgram.getImageBase());
            line("");
            line("== INTERESTING STRINGS AND XREFS ==");
            ReferenceManager refs = currentProgram.getReferenceManager();
            Listing listing = currentProgram.getListing();
            for (Data data : listing.getDefinedData(true)) {
                Object value = data.getValue();
                if (!(value instanceof String)) continue;
                String s = (String)value;
                if (!interestingString(s)) continue;
                line("STRING " + data.getAddress() + " " + s.replace("\n", "\\n"));
                ReferenceIterator it = refs.getReferencesTo(data.getAddress());
                while (it.hasNext()) {
                    Reference r = it.next();
                    Address from = r.getFromAddress();
                    line("  XREF " + from + " " + functionAt(from) + " type=" + r.getReferenceType());
                }
            }

            line("");
            line("== IMMEDIATE CANDIDATES IN EXECUTABLE MEMORY ==");
            int count = 0;
            for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
                if (!block.isExecute()) continue;
                AddressSet blockSet = new AddressSet(block.getStart(), block.getEnd());
                for (Instruction ins : listing.getInstructions(blockSet, true)) {
                    boolean hit = false;
                    StringBuilder scalars = new StringBuilder();
                    for (int op = 0; op < ins.getNumOperands(); op++) {
                        for (Object obj : ins.getOpObjects(op)) {
                            if (!(obj instanceof Scalar)) continue;
                            Scalar scalar = (Scalar)obj;
                            long v = scalar.getUnsignedValue();
                            if (CONSTANTS.contains(v)) {
                                if (scalars.length() != 0) scalars.append(',');
                                scalars.append("0x").append(Long.toHexString(v));
                                hit = true;
                            }
                        }
                    }
                    if (!hit) continue;
                    String m = ins.getMnemonicString().toUpperCase();
                    if (!(m.startsWith("CMP") || m.startsWith("TEST") || m.startsWith("AND") ||
                          m.startsWith("MOV") || m.startsWith("SUB") || m.startsWith("ADD") ||
                          m.startsWith("LEA"))) continue;
                    line(ins.getAddress() + " " + functionAt(ins.getAddress()) +
                         " constants=" + scalars + " :: " + ins);
                    count++;
                    if (count >= 20000) {
                        line("TRUNCATED at 20000 immediate candidates");
                        break;
                    }
                }
                if (count >= 20000) break;
            }
            line("candidate_count=" + count);
        }
        finally {
            out.close();
        }
        println("output=" + output.getAbsolutePath());
    }
}
