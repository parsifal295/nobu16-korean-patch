// Print functions that reference every supplied target address.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import java.util.HashSet;
import java.util.Set;
import java.util.TreeSet;

public class IntersectTargetCallers extends GhidraScript {
    private Set<Address> callers(Address target) {
        Set<Address> out = new HashSet<>();
        ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(target);
        while (refs.hasNext()) {
            Reference ref = refs.next();
            Function f = getFunctionContaining(ref.getFromAddress());
            if (f != null) out.add(f.getEntryPoint());
        }
        return out;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) throw new IllegalArgumentException("two or more targets required");
        Set<Address> result = null;
        for (String arg : args) {
            Address target = currentProgram.getAddressFactory().getAddress(arg);
            Set<Address> set = callers(target);
            println("TARGET " + target + " CALLERS " + set.size());
            if (result == null) result = set;
            else result.retainAll(set);
        }
        TreeSet<Address> sorted = new TreeSet<>(result);
        println("INTERSECTION " + sorted.size());
        for (Address entry : sorted) {
            Function f = getFunctionAt(entry);
            println(entry + " " + (f == null ? "<none>" : f.getName()));
        }
    }
}
