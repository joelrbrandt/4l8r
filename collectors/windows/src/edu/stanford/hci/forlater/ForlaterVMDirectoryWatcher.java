package edu.stanford.hci.forlater;

import java.io.File;

public class ForlaterVMDirectoryWatcher extends AbstractDirectoryWatcher {

	private static final String VM_EXTENSION = ".mp3";

	public ForlaterVMDirectoryWatcher(File directory, File doneDirectory) {
		super(directory, doneDirectory, new String[] { VM_EXTENSION });
	}

	@Override
	public boolean processFile(File f) {
		String[] s = f.getName().split("[_\\.]");
		if (s.length >= 4) {
			if (!(ForlaterProcessor.addEntry(s[2], null, f, null))) {
				ForlaterProcessor.log("Error: didn't add audio snippet at \"" + f.getAbsolutePath() + "\"" );
				return false;
			}
			else {
				ForlaterProcessor.log("Success: added audio snippet at \"" + f.getAbsolutePath() + "\"" );
				return true;
			}
		}
		else {
			ForlaterProcessor.log("Error: didn't add audio snippet at \"" + f.getAbsolutePath() + "\"" );
			return false;
		}
	}

}
