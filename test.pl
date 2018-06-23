use threads;
my @threads; 


# We invoke COFFE to carry out several sets of simulations and then check the results to be in the expected range


# Settings:
# Do you want BRAM simulations?
$include_BRAM = 1;
# You can change what test cases you want here:
if ($include_BRAM == 1){
# Test cases using BRAM:
	@test_cases = ("RAM32", "MTJ32");
}
else{
# Test cases without BRAM:
	@test_cases = ("bulk_example");
}


# COFFE invokations:
foreach (@test_cases) {
$command = "perl invoke.pl $_ $include_BRAM";
print("Invoking COFFE for ".$_."\n");
push @threads, threads->new('msc',$command);
}



foreach (@threads) {
   $_->join();
}

# Expected results:
@tile_area_results= (1000,1000);
@BRAM_area_results= (7800,3400);

# Check results:

for my $i (0 .. $#test_cases) {
$command = "perl checkresults.pl $test_cases[$i]  $tile_area_results[$i]  $BRAM_area_results[$i]";
print("Checking results for ".$test_cases[$i]."\n");
push @threads, threads->new('msc',$command);
}

foreach (@threads) {
   $_->join();
}

sub msc{
	system(@_);
}
