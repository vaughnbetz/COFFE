

$test_case = $ARGV[0];	
$BRAM_enabled = $ARGV[1];

if ($BRAM_enabled == 1){
$full_command = "python coffe.py -i 6 -q 0.03 input_files/BRAM/".$test_case.".txt >log_".$test_case.".txt";
system($full_command);
}
else
{
$full_command = "python coffe.py -i 6 -q 0.03 input_files/".$test_case.".txt >log_".$test_case.".txt";
system($full_command);
}

