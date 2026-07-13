// @category NOBU16
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;

public class DisassembleRange extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException("start address and instruction count required");
        }
        Address address = currentProgram.getAddressFactory().getAddress(args[0]);
        int count = Integer.decode(args[1]);
        Instruction instruction = getInstructionContaining(address);
        if (instruction == null) instruction = getInstructionAt(address);
        for (int i = 0; i < count && instruction != null; i++) {
            println(instruction.getAddress() + "  " + instruction + "  bytes=" +
                ghidra.util.NumericUtilities.convertBytesToString(instruction.getBytes()));
            instruction = instruction.getNext();
        }
    }
}
