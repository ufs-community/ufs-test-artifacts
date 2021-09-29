#!/usr/bin/perl

$esmf_dir = @ARGV[0];
$hpc_stack_dir = @ARGV[1];
$hpc_modules_dir = @ARGV[2];
$ufs_artifacts_dir = @ARGV[3];
chdir $esmf_dir;
@gitlines = split(/\n/,`git remote update 2>&1`);
#@gitlines[0] = " * [new tag]         ESMF_8_2_0_beta_snapshot_14 -> ESMF_8_1_1_beta_snapshot_02";
chdir $hpc_stack_dir;
foreach(@gitlines) {
  print("line is $_\n");
  if($_ =~ /new tag/) {
    @words = split(/\s+/,$_);
    print("words are @words\n");
    $tag = @words[4];
    $tag =~ s/ESMF_//g;
    system("cp config/stack_esmf_template.yaml config/stack_esmf.yaml");
    system("sed -i 's/ESMFTAG/$tag/g' config/stack_esmf.yaml");
    system("sed -i 's/ESMFDEBUG/NO/g' config/stack_esmf.yaml");
    system("./build_stack.sh -p $hpc_modules_dir -c config/config_hera.sh -y config/stack_esmf.yaml -m");

    system("$ufs_artifacts_dir/rebuild_s2s.sh $tag");
  }
}

