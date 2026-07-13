// @category NOBU16
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import java.nio.charset.StandardCharsets;

public class FindStringXrefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) throw new IllegalArgumentException("ASCII strings required");
        Memory memory = currentProgram.getMemory();
        for (String needle : args) {
            byte[] bytes = needle.getBytes(StandardCharsets.US_ASCII);
            Address cursor = memory.getMinAddress();
            println("NEEDLE " + needle);
            while (cursor != null && cursor.compareTo(memory.getMaxAddress()) <= 0) {
                Address hit = memory.findBytes(cursor, memory.getMaxAddress(), bytes, null, true, monitor);
                if (hit == null) break;
                println(" HIT " + hit);
                ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(hit);
                while (refs.hasNext()) {
                    Reference ref = refs.next();
                    Function function = getFunctionContaining(ref.getFromAddress());
                    println("  REF " + ref.getFromAddress() + " " +
                        (function == null ? "<no-function>" : function.getName() + "@" + function.getEntryPoint()));
                }
                cursor = hit.add(1);
            }
        }
    }
}
