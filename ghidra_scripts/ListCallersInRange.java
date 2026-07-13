// List unique callers of a target function, limited to an address range.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ListCallersInRange extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 3) {
            throw new IllegalArgumentException("target start end");
        }
        Address target = currentProgram.getAddressFactory().getAddress(args[0]);
        Address start = currentProgram.getAddressFactory().getAddress(args[1]);
        Address end = currentProgram.getAddressFactory().getAddress(args[2]);
        Map<Address, List<Address>> callers = new HashMap<>();
        ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(target);
        while (refs.hasNext()) {
            Reference ref = refs.next();
            Function f = currentProgram.getFunctionManager().getFunctionContaining(ref.getFromAddress());
            if (f == null) continue;
            Address entry = f.getEntryPoint();
            if (entry.compareTo(start) < 0 || entry.compareTo(end) > 0) continue;
            callers.computeIfAbsent(entry, k -> new ArrayList<>()).add(ref.getFromAddress());
        }
        List<Address> entries = new ArrayList<>(callers.keySet());
        Collections.sort(entries);
        for (Address entry : entries) {
            Function f = currentProgram.getFunctionManager().getFunctionAt(entry);
            List<Address> sites = callers.get(entry);
            Collections.sort(sites);
            println(entry + " " + (f == null ? "<none>" : f.getName()) +
                " size=" + (f == null ? 0 : f.getBody().getNumAddresses()) +
                " calls=" + sites);
        }
        println("UNIQUE " + entries.size());
    }
}
