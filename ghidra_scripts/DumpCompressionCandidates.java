// Finds code and string references that are useful when locating the NOBU16
// message-container decompressor. Run after normal auto-analysis.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.StringDataInstance;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.LinkedHashSet;
import java.util.Locale;
import java.util.Set;

public class DumpCompressionCandidates extends GhidraScript {
    private static final long[] CONSTANTS = {
        0x7ffaL, 0x7ffeL, 0xc1c4L, 0x3546L, 0xc1c40101L, 0x35460101L
    };

    private static final String[] WORDS = {
        "compress", "decompress", "inflate", "deflate", "unpack", "decode",
        "msggame", "msgdata", "msgui", "res_lang", ".bin"
    };

    @Override
    protected void run() throws Exception {
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        long functionCount = 0;
        while (functions.hasNext()) {
            functions.next();
            functionCount++;
        }
        println("PROGRAM=" + currentProgram.getName());
        println("FUNCTIONS=" + functionCount);

        Set<Function> candidates = new LinkedHashSet<>();
        println("== STRING/XREF HITS ==");
        for (Data data : currentProgram.getListing().getDefinedData(true)) {
            if (!StringDataInstance.isString(data)) {
                continue;
            }
            String value = StringDataInstance.getStringDataInstance(data).getStringValue();
            if (value == null) {
                continue;
            }
            String lower = value.toLowerCase(Locale.ROOT);
            boolean interesting = false;
            for (String word : WORDS) {
                if (lower.contains(word)) {
                    interesting = true;
                    break;
                }
            }
            if (!interesting) {
                continue;
            }
            println("STRING " + data.getAddress() + " " + value.replace('\n', ' '));
            ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(data.getAddress());
            while (references.hasNext()) {
                Reference reference = references.next();
                Address from = reference.getFromAddress();
                Function function = currentProgram.getFunctionManager().getFunctionContaining(from);
                println("  XREF " + from + " " + (function == null ? "<no-function>" : function.getName()));
                if (function != null) {
                    candidates.add(function);
                }
            }
        }

        println("== SCALAR HITS ==");
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
                for (Object object : instruction.getOpObjects(operand)) {
                    if (!(object instanceof Scalar)) {
                        continue;
                    }
                    long value = ((Scalar) object).getUnsignedValue();
                    for (long wanted : CONSTANTS) {
                        if (value != wanted) {
                            continue;
                        }
                        Function function = currentProgram.getFunctionManager()
                            .getFunctionContaining(instruction.getAddress());
                        println(String.format("SCALAR %s 0x%x %s %s",
                            instruction.getAddress(), value,
                            function == null ? "<no-function>" : function.getName(),
                            instruction));
                        if (function != null) {
                            candidates.add(function);
                        }
                    }
                }
            }
        }

        println("== UNIQUE CANDIDATE FUNCTIONS ==");
        for (Function function : candidates) {
            println(function.getEntryPoint() + " " + function.getName() +
                " size=" + function.getBody().getNumAddresses());
        }
        println("CANDIDATE_COUNT=" + candidates.size());
    }
}
