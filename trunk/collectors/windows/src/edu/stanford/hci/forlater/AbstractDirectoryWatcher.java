package edu.stanford.hci.forlater;

import java.io.File;
import java.io.FileFilter;
import java.util.Date;

public abstract class AbstractDirectoryWatcher extends Thread {
	// we don't process files that have been modified in the last COOL_OFF_TIME milliseconds
	private static final long COOL_OFF_TIME = 10L * 1000L;
	private static final long SLEEP_DELAY = 10L * 1000L; 

	private File directory;
	private File doneDirectory;
	private String[] extensions;

	public AbstractDirectoryWatcher(File directory, File doneDirectory, String[] extensions) {
		if (!directory.isDirectory()) {
			throw new IllegalArgumentException("Must specify a valid directory when creating a Directory Watcher");
		}
		if (!directory.isDirectory()) {
			throw new IllegalArgumentException("Must specify a valid done directory when creating a Directory Watcher");
		}
		this.directory = directory;
		this.doneDirectory = doneDirectory;
		this.extensions = extensions;
	}

	public void run() {
		while (true) {
			final long latest = (new Date()).getTime() - COOL_OFF_TIME;
			FileFilter filter = new FileFilter() {
				public boolean accept(File f) {
					if (f.isFile()) {
						long modifiedTime = f.lastModified();
						if (modifiedTime < latest) {
							String lowercaseFilename = f.getName().toLowerCase();
							for (String ext : extensions) {
								if (lowercaseFilename.endsWith(ext)) {
									return true;
								}
							}
						}
					}
					return false;
				}
			};
			File[] toProcess = directory.listFiles(filter);
			if (toProcess.length > 0)
				processFiles(toProcess);

			try {
				Thread.sleep(SLEEP_DELAY);
			} catch (InterruptedException e) { }
		}
	}

	private void processFiles(File[] toProcess) {
		// process files until the concrete implementation returns false on a file
		for (File f : toProcess) {
			try {
				if (processFile(f)) {
					if (!(f.renameTo(new File(doneDirectory.getAbsolutePath(), f.getName())))) {
						ForlaterProcessor.log("Error: could not move file " + f.getAbsolutePath());
					}
				} else {
					break;
				}
			} catch(Exception e) {
				ForlaterProcessor.log("Unknown error processing \"" + f.getName() + "\" :" + e.getMessage());
			}
			try { // to make sure we don't have anything with the same filename
				Thread.sleep(1250);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}

	abstract public boolean processFile(File f);

	File getDirectory() {
		return directory;
	}
}
