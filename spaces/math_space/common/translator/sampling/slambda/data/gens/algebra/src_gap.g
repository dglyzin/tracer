# Read("src_gap.g");
# s5 := Group((1,2), (1,2,3,4,5));
# gap> subg5:=AllSubgroups(s5);
# gap> subg5_nab := Filtered(subg5, g -> not IsAbelian(g));
# gap> subg5_ab := Filtered(subg5, IsAbelian);
# gap> subg5_ab_unt:=Filtered(subg5_ab, g -> Length(AllSubgroups(g))>2);
# gap> subg5_nab_unt:=Filtered(subg5_nab, g -> Length(AllSubgroups(g))>2);
# gap> subg5_nab_unt[17];Filtered(AllSubgroups(subg5_nab_unt[17]), IsAbelian);
# gap> subg5_nab_unt[17];Filtered(AllSubgroups(subg5_nab_unt[17]), g -> not IsAbelian(g));

