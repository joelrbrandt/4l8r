package edu.stanford.hci.forlater;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashSet;

import javax.sound.sampled.AudioFileFormat;
import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.DataLine;
import javax.sound.sampled.LineUnavailableException;
import javax.sound.sampled.TargetDataLine;

import com.skype.Call;
import com.skype.CallAdapter;
import com.skype.CallStatusChangedListener;
import com.skype.Skype;
import com.skype.SkypeException;
import com.skype.VoiceMail;
import com.skype.VoiceMailListener;
import com.skype.VoiceMailStatusChangedListener;
import com.skype.VoiceMail.Status;

public class ForlaterVoicemailRecorder {

	public static final String DIRECTORY_INCOMING = "c:\\diary\\vm\\incoming\\";
	public static final String DIRECTORY_FINAL = "c:\\diary\\vm\\";
	public static final File PROCESSED_VMS_LIST = new File(DIRECTORY_INCOMING + "processed.obj");
	public static final SimpleDateFormat DATE_FORMAT_FOR_FILE = 
		new SimpleDateFormat("yyyyMMdd_HHmmss");
	public static final SimpleDateFormat DATE_FORMAT_FOR_LOG = 
		new SimpleDateFormat("MM/dd/yyyy HH:mm:ss");

	private HashSet<String> processedVoiceMails;
	private boolean initialized;

	private void checkForNewVoicemails() throws SkypeException {
		VoiceMail[] vms = Skype.getAllVoiceMails();
		for (VoiceMail vm : vms) {
			
			Date timestamp = vm.getStartTime();
			String from = vm.getPartnerId();
			String filePrefix = DATE_FORMAT_FOR_FILE.format(timestamp) + "_" + (from.length() > 10 ? from.substring(from.length() - 10) : from);
			if (!processedVoiceMails.contains(filePrefix)) {
				if (recordVoiceMailToFile(vm, filePrefix))  {
					processedVoiceMails.add(filePrefix);
					writeProcessedVoiceMailsFile(processedVoiceMails);
				}
			}

		}
	}

	private boolean recordVoiceMailToFile(VoiceMail vm, String filePrefix) throws SkypeException {
		boolean result = false;

		final String wavFilename = DIRECTORY_INCOMING + filePrefix + ".wav";
		final String mp3Filename = DIRECTORY_FINAL + filePrefix + ".mp3";

		final SimpleAudioRecorder recorder = getNewRecorder(wavFilename);

		vm.addVoiceMailStatusChangedListener(new VoiceMailStatusChangedListener() {
			boolean started = false;
			
			public void statusChanged(Status status) throws SkypeException {
				if (!started && status == Status.PLAYING) {
					recorder.start();
					started = true;
				} else if (status == Status.PLAYED) {
					recorder.stopRecording();
				}
			}

		});

		vm.startPlayback();

		int count = 0;
		while (!recorder.isRecording() && count < 40) { // wait at least 10 seconds for recording to start
			try {
				Thread.sleep(250);
				count++;
			} catch (InterruptedException e) { }
		}

		count = 0;
		while (recorder.isRecording() && count < 4 * 60) { // wait at least 60 seconds for recording to stop, otherwise stop it
			try {
				Thread.sleep(250);
				count++;
			} catch (InterruptedException e) { }
		}

		if (recorder.isRecording())
			recorder.stopRecording();

		if (recorder.didRecord()) {
			Process proc = null;
			System.out.println("Starting encoding of " + mp3Filename);
			String[] procArgs = { "c:\\lame\\lame.exe", "-b", "48", "--resample", "22.05", "--quiet", wavFilename, mp3Filename };
			try {
				proc = Runtime.getRuntime().exec(procArgs);
			} catch (IOException e) {
				e.printStackTrace();
			}

			if (proc != null) {
				InputStream is = proc.getInputStream();
				byte[] buf = new byte[100];
				while (true) {
					try {
						if (is.read(buf) < 0) { // reached EOF, the process completed
							break;
						}
					} catch (IOException e) {
						break;
					}
				}
			}

			if (proc != null) {
				System.out.println("Finished encoding of " + mp3Filename + " with exit code " + proc.exitValue());
				if (proc.exitValue() == 0) { // recording was successful!
					result = true;
				}
			}
			else {
				System.out.println("Error: could not create process to encode " + mp3Filename);
			}	
		}
		
		return result;
	}

	public ForlaterVoicemailRecorder() {

		processedVoiceMails = readProcessedVoiceMailsFile();

		VoiceMailListener vml = new VoiceMailListener() {
			public void voiceMailMade(VoiceMail madeVoiceMail) { }

			public void voiceMailReceived(VoiceMail receivedVoiceMail) {
				try {
					System.out.println("We've recevied a voicemail: ID: " + receivedVoiceMail.getId() + " From: " + receivedVoiceMail.getPartnerId());
				} catch (SkypeException e) {
					e.printStackTrace();
				}
			}	
		};

		CallAdapter ca = new CallAdapter() {
			public void callReceived(Call call) {
				final Call incomingCall = call;
				System.out.println("Call received");
				call.addCallStatusChangedListener(new CallStatusChangedListener(){
					public void statusChanged(Call.Status status) {
						System.out.println(status);
						if (status == Call.Status.RINGING){
							System.out.println("Call ringing -- redirecting to VM");
							try {
								incomingCall.redirectToVoiceMail();
							} catch (SkypeException e) {
								e.printStackTrace();
							}

						}
					}
				});
			}
		};

		try {
			Skype.setDebug(false);
			Skype.addVoiceMailListener(vml);
			Skype.addCallListener(ca);
			initialized = true;
		} catch (SkypeException e) {
			e.printStackTrace();
		}
	}

	@SuppressWarnings("unchecked")
	private HashSet<String> readProcessedVoiceMailsFile() {
		HashSet<String> result = null;
		try {
			if (PROCESSED_VMS_LIST.exists()) {
				if (PROCESSED_VMS_LIST.canRead()) {
					FileInputStream fis = new FileInputStream(PROCESSED_VMS_LIST);
					ObjectInputStream ois = new ObjectInputStream(fis);
					result = (HashSet<String>) ois.readObject();
					ois.close();
					System.out.println("Successfully read in processed voicemails file!");
				} else {
					System.out.println("Processed voicemails file exists, but cannot read from it");
				}
			} else {
				System.out.println("Processed voicemail file does not exist -- will return new empty set");
			}
		} catch (Exception e) {
			System.out.println("Error reading processed voicemaials file");
			e.printStackTrace();
		} finally {
			if (result == null)
				result = new HashSet<String>();
		}
		
		return result;
	}

	private void writeProcessedVoiceMailsFile(HashSet<String> hs) {
		try {
			if (!PROCESSED_VMS_LIST.exists() || PROCESSED_VMS_LIST.canWrite()) {
				FileOutputStream fos = new FileOutputStream(PROCESSED_VMS_LIST);
				ObjectOutputStream oos = new ObjectOutputStream(fos);
				oos.writeObject(hs);
				oos.close();
				System.out.println("Successfully wrote processed voicemails file!");
			} else {
				System.out.println("Cannot write to processed voicemails file");
			}
		} catch (Exception e) {
			System.out.println("Error writing processed voicemails file");
			e.printStackTrace();
		}
		
	}
	
	public SimpleAudioRecorder getNewRecorder(String filename) {

		File outputFile = new File(filename);

		AudioFormat	audioFormat = new AudioFormat(
				AudioFormat.Encoding.PCM_SIGNED,
				44100.0F, 16, 2, 4, 44100.0F, false);

		DataLine.Info info = new DataLine.Info(TargetDataLine.class, audioFormat);
		TargetDataLine targetDataLine = null;
		try
		{
			targetDataLine = (TargetDataLine) AudioSystem.getLine(info);
			targetDataLine.open(audioFormat);
		}
		catch (LineUnavailableException e)
		{
			System.out.println("Error: Unable to get a recording line");
			e.printStackTrace();
			return null;
		}

		AudioFileFormat.Type targetType = AudioFileFormat.Type.WAVE;

		SimpleAudioRecorder	recorder = new SimpleAudioRecorder(
				targetDataLine,
				targetType,
				outputFile);

		return recorder;

	}

	public boolean isInitialized() {
		return initialized;
	}

	public static void main(String[] args) {
		System.out.println("Starting up the 4l8r Voicemail Recorder...");

		ForlaterVoicemailRecorder fvr = null;
		fvr = new ForlaterVoicemailRecorder();
		if (fvr.isInitialized()) {
			System.out.println("... initialized and running!");
		} else {
			System.out.println("... error initializing 4l8r Voicemail Recorder, exiting. ");
			System.exit(-1);
		}
		while(true) {
			try {		
				if (fvr != null) {
					fvr.checkForNewVoicemails();
				}
				Thread.sleep(10000);
			}
			catch (InterruptedException e) {}
			catch (SkypeException e) {
				System.out.println("Error checking for new voicemails:");
				e.printStackTrace();
			}
		}
	}
}

