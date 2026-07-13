// @category NOBU16
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;

public class DumpMemory extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("address and byte count required");
        Address address = currentProgram.getAddressFactory().getAddress(args[0]);
        int count = Integer.decode(args[1]);
        byte[] bytes = new byte[count];
        currentProgram.getMemory().getBytes(address, bytes);
        println(address + " " + ghidra.util.NumericUtilities.convertBytesToString(bytes));
    }
}
