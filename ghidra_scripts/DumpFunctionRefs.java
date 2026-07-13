// @category NOBU16
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class DumpFunctionRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        for (String arg : getScriptArgs()) {
            Address address = currentProgram.getAddressFactory().getAddress(arg);
            Function target = getFunctionContaining(address);
            Address entry = target == null ? address : target.getEntryPoint();
            println("TARGET " + arg + " entry=" + entry + " name=" +
                (target == null ? "<none>" : target.getName()));
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(entry);
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function caller = getFunctionContaining(ref.getFromAddress());
                println(" REF " + ref.getFromAddress() + " " +
                    (caller == null ? "<none>" : caller.getName() + "@" + caller.getEntryPoint()));
            }
        }
    }
}
