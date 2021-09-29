#!/usr/bin/perl

chdir "/scratch1/NCEPDEV/da/Mark.Potts/sandbox/esmf";
@gitlines = split(/\n/,`git remote update 2>&1`);
#@gitlines[0] = " * [new tag]         ESMF_8_2_0_beta_snapshot_14 -> ESMF_8_1_1_beta_snapshot_02";
chdir "/scratch1/NCEPDEV/da/Mark.Potts/sandbox/hpc-stack";
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
    system("./build_stack.sh -p /scratch1/NCEPDEV/da/Mark.Potts/sandbox/hpc-modules -c config/config_hera.sh -y config/stack_esmf.yaml -m");

    system("/home/Mark.Potts/rebuild_s2s.sh $tag");
  }
}

