#!/usr/bin/perl

$esmf_dir = @ARGV[0];
$hpc_stack_dir = @ARGV[1];
$hpc_modules_dir = @ARGV[2];
$ufs_artifacts_dir = @ARGV[3];
chdir $esmf_dir;
@gitlines = split(/\n/,`git remote update 2>&1`);
#@gitlines[0] = " * [new tag]         ESMF_8_2_0_beta_snapshot_19 -> ESMF_8_1_1_beta_snapshot_19";
chdir $hpc_stack_dir;
foreach(@gitlines) {
  print("line is $_\n");
  if($_ =~ /new tag/) {
    @words = split(/\s+/,$_);
    print("words are @words\n");
    $tag = @words[4];
    $tag =~ s/ESMF_//g;
    system("cp stack/stack_esmf_template.yaml stack/stack_noaa.yaml");
    system("sed -i 's/ESMFTAG/$tag/g' stack/stack_noaa.yaml");
    system("./build_standalone_esmf.sh");
  }
}

