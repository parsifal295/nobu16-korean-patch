// List references to one or more addresses and their containing functions.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class ListFunctionReferences extends GhidraScript {
    @Override
    public void run() throws Exception {
        for (String arg : getScriptArgs()) {
            Address target = currentProgram.getAddressFactory().getAddress(arg);
            println("TARGET " + target);
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(target);
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Address from = ref.getFromAddress();
                Function f = currentProgram.getFunctionManager().getFunctionContaining(from);
                String fn = f == null ? "<no-function>" : f.getName() + "@" + f.getEntryPoint();
                println("  " + from + " " + fn + " " + ref.getReferenceType());
            }
        }
    }
}
