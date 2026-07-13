// List references into an address range, including references to interior
// members of a pointer/configuration table.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class ListRangeReferences extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException("start and end address required");
        }
        Address start = currentProgram.getAddressFactory().getAddress(args[0]);
        Address end = currentProgram.getAddressFactory().getAddress(args[1]);
        for (Address target = start; target.compareTo(end) <= 0; target = target.add(1)) {
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(target);
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Address from = ref.getFromAddress();
                Function fn = currentProgram.getFunctionManager().getFunctionContaining(from);
                println(target + " <- " + from + " " +
                    (fn == null ? "<no-function>" : fn.getName() + "@" + fn.getEntryPoint()) +
                    " " + ref.getReferenceType());
            }
        }
    }
}
