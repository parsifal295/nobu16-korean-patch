// Search the unpacked NOBU16 executable for likely language/font range gates.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

import java.io.File;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class FindFontGateCandidates extends GhidraScript {
    private static final Set<Long> INTERESTING = new HashSet<>(Arrays.asList(
        0xd7L, 0xd8L, 0xffL, 0x100L, 0x7fffL, 0x8000L,
        0xffffL, 0x10000L, 0x1ffffL, 0x20000L, 0xac00L
    ));

    private PrintWriter out;

    private void line(String text) {
        out.println(text);
        println(text);
    }

    private String functionAt(Address address) {
        Function function = getFunctionContaining(address);
        if (function == null) return "<no-function>";
        return function.getName() + "@" + function.getEntryPoint();
    }

    private void dumpNamedReferences(String needle) {
        SymbolIterator symbols = currentProgram.getSymbolTable().getAllSymbols(true);
        while (symbols.hasNext() && !monitor.isCancelled()) {
            Symbol symbol = symbols.next();
            if (!symbol.getName().toLowerCase().contains(needle.toLowerCase())) continue;
            line("SYMBOL " + symbol.getName(true) + " @ " + symbol.getAddress());
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(symbol.getAddress());
            while (refs.hasNext()) {
                Reference ref = refs.next();
                line("  REF " + ref.getFromAddress() + " " + functionAt(ref.getFromAddress()));
            }
        }
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        File report = new File(args.length > 0 ? args[0] : "font_gate_candidates.txt");
        report.getParentFile().mkdirs();
        out = new PrintWriter(report, "UTF-8");
        try {
            line("PROGRAM " + currentProgram.getName());
            dumpNamedReferences("WideCharToMultiByte");
            dumpNamedReferences("MultiByteToWideChar");
            dumpNamedReferences("res_lang");

            InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
            while (instructions.hasNext() && !monitor.isCancelled()) {
                Instruction instruction = instructions.next();
                String mnemonic = instruction.getMnemonicString().toUpperCase();
                if (!(mnemonic.startsWith("CMP") || mnemonic.startsWith("TEST") ||
                      mnemonic.startsWith("AND") || mnemonic.startsWith("MOV") ||
                      mnemonic.startsWith("LEA"))) continue;

                boolean hit = false;
                StringBuilder values = new StringBuilder();
                for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
                    for (Object object : instruction.getOpObjects(operand)) {
                        if (!(object instanceof Scalar)) continue;
                        Scalar scalar = (Scalar)object;
                        long unsigned = scalar.getUnsignedValue();
                        if (!INTERESTING.contains(unsigned)) continue;
                        hit = true;
                        if (values.length() > 0) values.append(',');
                        values.append("0x").append(Long.toHexString(unsigned));
                    }
                }
                if (hit) {
                    line("SCALAR " + instruction.getAddress() + " " + functionAt(instruction.getAddress()) +
                         " values=" + values + " :: " + instruction);
                }
            }
        } finally {
            out.close();
        }
    }
}
