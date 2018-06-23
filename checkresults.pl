
$test_case = $ARGV[0];	
$expected_result_area = $ARGV[1];
$expected_results_ram = $ARGV[2];


if (open (FILE, "log_".$test_case.".txt")){  
	# Read out whatever results you are interested in:
	while (<FILE>) {
		chomp;
		 my($line) = $_;
		 #print($_."\n");
		 if ($line =~ /  RAM               (\S+)/){
		 	$ram_area = $1;
		 }

		 if ($line =~ /  Tile Area                            (\S+)/){
		 	$tile_area = $1;
		 }
	}
}else{ 
die "Error opening log file - $!\n";
	return 0;
}

# Speculation of the expected results:

# Check tile area with 20% tolerance:
if ($tile_area> 1.2 * $expected_result_area || $tile_area < 0.8 * $expected_result_area)
{
die "Error: Tile area outside of expected range \n";
}else{
print("results for ".$test_case." logic area are in the expected range. \n");
}

# Check BRAM area with 20% tolerance:
if ($ram_area> 1.2 * $expected_results_ram || $ram_area < 0.8 * $expected_results_ram)
{
die "Error: BRAM area outside of expected range \n";
}else{
print("results for ".$test_case." BRAM area are in the expected range. \n");
}
