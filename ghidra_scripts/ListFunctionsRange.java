// List functions whose entry points fall within an inclusive address range.
// @category NOBU16

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

public class ListFunctionsRange extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException("start end");
        }
        Address start = currentProgram.getAddressFactory().getAddress(args[0]);
        Address end = currentProgram.getAddressFactory().getAddress(args[1]);
        FunctionIterator it = currentProgram.getFunctionManager()
            .getFunctions(new AddressSet(start, end), true);
        while (it.hasNext()) {
            Function f = it.next();
            println(f.getEntryPoint() + " " + f.getName() + " size=" + f.getBody().getNumAddresses());
        }
    }
}
