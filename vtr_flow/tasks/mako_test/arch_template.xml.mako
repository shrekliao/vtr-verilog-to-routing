<!-- 
  Architecture with no fracturable LUTs

  - 40 nm technology
  - General purpose logic block: 
    K = ${int(K)}, N = ${int(N)}
  - Routing architecture: L = ${int(L)}, fc_in = ${fcin}, Fc_out = ${fcout}, fs = ${int(fs)}

  Details on Modelling:

  Based on flagship k6_frac_N10_mem32K_40nm.xml architecture.  This architecture has no fracturable LUTs nor any heterogeneous blocks.
  Fix the Tiles to 4x4


  Authors: Cheng-Chieh, Liao
-->
<architecture>
  <!-- 
       ODIN II specific config begins 
       Describes the types of user-specified netlist blocks (in blif, this corresponds to 
       ".model [type_of_block]") that this architecture supports.

       Note: Basic LUTs, I/Os, and flip-flops are not included here as there are 
       already special structures in blif (.names, .input, .output, and .latch) 
       that describe them.
  -->
  <models>
  </models>
  <tiles>
    <tile name="io" area="0">
      <sub_tile name="io" capacity="8">
        <equivalent_sites>
          <site pb_type="io" pin_mapping="direct"/>
        </equivalent_sites>
        <input name="outpad" num_pins="1"/>
        <output name="inpad" num_pins="1"/>
        <clock name="clock" num_pins="1"/>
        <fc in_type="frac" in_val="${fcin}" out_type="frac" out_val="${fcout}"/>
        <pinlocations pattern="custom">
          <loc side="left">io.outpad io.inpad io.clock</loc>
          <loc side="top">io.outpad io.inpad io.clock</loc>
          <loc side="right">io.outpad io.inpad io.clock</loc>
          <loc side="bottom">io.outpad io.inpad io.clock</loc>
        </pinlocations>
      </sub_tile>
    </tile>
    <tile name="clb" area="53894">
      <sub_tile name="clb">
        <equivalent_sites>
          <site pb_type="clb" pin_mapping="direct"/>
        </equivalent_sites>
        <input name="I" num_pins="40" equivalent="full"/>
        <output name="O" num_pins="10" equivalent="instance"/>
        <clock name="clk" num_pins="1"/>
        <fc in_type="frac" in_val="${fcin}" out_type="frac" out_val="${fcout}"/>
        <pinlocations pattern="spread"/>
      </sub_tile>
    </tile>
  </tiles>
  <!-- ODIN II specific config ends -->
  <!-- Physical descriptions begin -->
  <layout>
    <fixed_layout name="4x4" width="4" height="4">
      <!--Perimeter of 'io' blocks with 'EMPTY' blocks at corners-->
      <perimeter type="io" priority="100"/>
      <corners type="EMPTY" priority="101"/>
      <!--Fill with 'clb'-->
      <fill type="clb" priority="10"/>
    </fixed_layout>
  </layout>
  <device>
    <!-- VB & JL: Using Ian Kuon's transistor sizing and drive strength data for routing, at 40 nm. Ian used BPTM 
			     models. We are modifying the delay values however, to include metal C and R, which allows more architecture
			     experimentation. We are also modifying the relative resistance of PMOS to be 1.8x that of NMOS
			     (vs. Ian's 3x) as 1.8x lines up with Jeff G's data from a 45 nm process (and is more typical of 
			     45 nm in general). I'm upping the Rmin_nmos from Ian's just over 6k to nearly 9k, and dropping 
			     RminW_pmos from 18k to 16k to hit this 1.8x ratio, while keeping the delays of buffers approximately
			     lined up with Stratix IV. 
			     We are using Jeff G.'s capacitance data for 45 nm (in tech/ptm_45nm).
			     Jeff's tables list C in for transistors with widths in multiples of the minimum feature size (45 nm).
			     The minimum contactable transistor is 2.5 * 45 nm, so I need to multiply drive strength sizes in this file
	                     by 2.5x when looking up in Jeff's tables.
			     The delay values are lined up with Stratix IV, which has an architecture similar to this
			     proposed FPGA, and which is also 40 nm 
			     C_ipin_cblock: input capacitance of a track buffer, which VPR assumes is a single-stage
			     4x minimum drive strength buffer. -->
    <sizing R_minW_nmos="8926" R_minW_pmos="16067"/>
    <!-- The grid_logic_tile_area below will be used for all blocks that do not explicitly set their own (non-routing)
     	  area; set to 0 since we explicitly set the area of all blocks currently in this architecture file.
	  -->
    <area grid_logic_tile_area="0"/>
    <chan_width_distr>
      <x distr="uniform" peak="1.000000"/>
      <y distr="uniform" peak="1.000000"/>
    </chan_width_distr>
    <switch_block type="wilton" fs="${int(fs)}"/>
    <connection_block input_switch_name="ipin_cblock"/>
  </device>
  <switchlist>
    <!-- VB: the mux_trans_size and buf_size data below is in minimum width transistor *areas*, assuming the purple
	       book area formula. This means the mux transistors are about 5x minimum drive strength.
	       We assume the first stage of the buffer is 3x min drive strength to be reasonable given the large 
	       mux transistors, and this gives a reasonable stage ratio of a bit over 5x to the second stage. We assume
	       the n and p transistors in the first stage are equal-sized to lower the buffer trip point, since it's fed
	       by a pass transistor mux. We can then reverse engineer the buffer second stage to hit the specified 
	       buf_size (really buffer area) - 16.2x minimum drive nmos and 1.8*16.2 = 29.2x minimum drive.
	       I then took the data from Jeff G.'s PTM modeling of 45 nm to get the Cin (gate of first stage) and Cout 
	       (diff of second stage) listed below.  Jeff's models are in tech/ptm_45nm, and are in min feature multiples.
	       The minimum contactable transistor is 2.5 * 45 nm, so I need to multiply the drive strength sizes above by 
	       2.5x when looking up in Jeff's tables.
	       Finally, we choose a switch delay (58 ps) that leads to length 4 wires having a delay equal to that of SIV of 126 ps.
	       This also leads to the switch being 46% of the total wire delay, which is reasonable. -->
    <switch type="mux" name="0" R="551" Cin=".77e-15" Cout="4e-15" Tdel="58e-12" mux_trans_size="2.630740" buf_size="27.645901"/>
    <!--switch ipin_cblock resistance set to yeild for 4x minimum drive strength buffer-->
    <switch type="mux" name="ipin_cblock" R="2231.5" Cout="0." Cin="1.47e-15" Tdel="7.247000e-11" mux_trans_size="1.222260" buf_size="auto"/>
  </switchlist>
  <segmentlist>
    <!--- VB & JL: using ITRS metal stack data, 96 nm half pitch wires, which are intermediate metal width/space.  
			     With the 96 nm half pitch, such wires would take 60 um of height, vs. a 90 nm high (approximated as square) Stratix IV tile so this seems
			     reasonable. Using a tile length of 90 nm, corresponding to the length of a Stratix IV tile if it were square. -->
    <segment freq="1.000000" length="4" type="unidir" Rmetal="101" Cmetal="22.5e-15">
      <mux name="0"/>
      <sb type="pattern">1 1 1 1 1</sb>
      <cb type="pattern">1 1 1 1</cb>
    </segment>
  </segmentlist>
  <complexblocklist>
    <!-- Define I/O pads begin -->
    <!-- Capacity is a unique property of I/Os, it is the maximum number of I/Os that can be placed at the same (X,Y) location on the FPGA -->
    <!-- Not sure of the area of an I/O (varies widely), and it's not relevant to the design of the FPGA core, so we're setting it to 0. -->
    <pb_type name="io">
      <input name="outpad" num_pins="1"/>
      <output name="inpad" num_pins="1"/>
      <clock name="clock" num_pins="1"/>
      <!-- IOs can operate as either inputs or outputs.
	     Delays below come from Ian Kuon. They are small, so they should be interpreted as
	     the delays to and from registers in the I/O (and generally I/Os are registered 
	     today and that is when you timing analyze them.
	     -->
      <mode name="inpad">
        <pb_type name="inpad" blif_model=".input" num_pb="1">
          <output name="inpad" num_pins="1"/>
        </pb_type>
        <interconnect>
          <direct name="inpad" input="inpad.inpad" output="io.inpad">
            <delay_constant max="4.243e-11" in_port="inpad.inpad" out_port="io.inpad"/>
          </direct>
        </interconnect>
      </mode>
      <mode name="outpad">
        <pb_type name="outpad" blif_model=".output" num_pb="1">
          <input name="outpad" num_pins="1"/>
        </pb_type>
        <interconnect>
          <direct name="outpad" input="io.outpad" output="outpad.outpad">
            <delay_constant max="1.394e-11" in_port="io.outpad" out_port="outpad.outpad"/>
          </direct>
        </interconnect>
      </mode>
      <!-- Every input pin is driven by 15% of the tracks in a channel, every output pin is driven by 10% of the tracks in a channel -->
      <!-- IOs go on the periphery of the FPGA, for consistency, 
          make it physically equivalent on all sides so that only one definition of I/Os is needed.
          If I do not make a physically equivalent definition, then I need to define 4 different I/Os, one for each side of the FPGA
        -->
      <!-- Place I/Os on the sides of the FPGA -->
      <power method="ignore"/>
    </pb_type>
    <!-- Define I/O pads ends -->
    <!-- Define general purpose logic block (CLB) begin -->
    <!--- Area calculation: Total Stratix IV tile area is about 8100 um^2, and a minimum width transistor 
	   area is 60 L^2 yields a tile area of 84375 MWTAs.
	   Routing at W=300 is 30481 MWTAs, leaving us with a total of 53000 MWTAs for logic block area 
	   This means that only 37% of our area is in the general routing, and 63% is inside the logic
	   block. Note that the crossbar / local interconnect is considered part of the logic block
	   area in this analysis. That is a lower proportion of of routing area than most academics
	   assume, but note that the total routing area really includes the crossbar, which would push
	   routing area up significantly, we estimate into the ~70% range. 
	   -->
    <pb_type name="clb">
      <input name="I" num_pins="40" equivalent="full"/>
      <output name="O" num_pins="10" equivalent="instance"/>
      <clock name="clk" num_pins="1"/>
      <!-- Describe basic logic element.  
             Each basic logic element has a ${int(K)}-LUT that can be optionally registered
        -->
      <pb_type name="fle" num_pb="10">
        <input name="in" num_pins="${int(K)}"/>
        <output name="out" num_pins="1"/>
        <clock name="clk" num_pins="1"/>
        <!-- ${int(K)}-LUT mode definition begin -->
        <mode name="n1_lut6">
          <!-- Define ${int(K)}-LUT mode -->
          <pb_type name="ble6" num_pb="1">
            <input name="in" num_pins="${int(K)}"/>
            <output name="out" num_pins="1"/>
            <clock name="clk" num_pins="1"/>
            <!-- Define LUT -->
            <pb_type name="lut6" blif_model=".names" num_pb="1" class="lut">
              <input name="in" num_pins="${int(K)}" port_class="lut_in"/>
              <output name="out" num_pins="1" port_class="lut_out"/>
              <!-- LUT timing using delay matrix -->
              <!-- These are the physical delay inputs on a Stratix IV LUT but because VPR cannot do LUT rebalancing,
                       we instead take the average of these numbers to get more stable results
                  82e-12
                  173e-12
                  261e-12
                  263e-12
                  398e-12
                  397e-12
                  -->
              <delay_matrix type="max" in_port="lut6.in" out_port="lut6.out">
                261e-12
                261e-12
                261e-12
                261e-12
                261e-12
                261e-12
              </delay_matrix>
            </pb_type>
            <!-- Define flip-flop -->
            <pb_type name="ff" blif_model=".latch" num_pb="1" class="flipflop">
              <input name="D" num_pins="1" port_class="D"/>
              <output name="Q" num_pins="1" port_class="Q"/>
              <clock name="clk" num_pins="1" port_class="clock"/>
              <T_setup value="66e-12" port="ff.D" clock="clk"/>
              <T_clock_to_Q max="124e-12" port="ff.Q" clock="clk"/>
            </pb_type>
            <interconnect>
              <direct name="direct1" input="ble6.in" output="lut6[0:0].in"/>
              <direct name="direct2" input="lut6.out" output="ff.D">
                <!-- Advanced user option that tells CAD tool to find LUT+FF pairs in netlist -->
                <pack_pattern name="ble6" in_port="lut6.out" out_port="ff.D"/>
              </direct>
              <direct name="direct3" input="ble6.clk" output="ff.clk"/>
              <mux name="mux1" input="ff.Q lut6.out" output="ble6.out">
                <!-- LUT to output is faster than FF to output on a Stratix IV -->
                <delay_constant max="25e-12" in_port="lut6.out" out_port="ble6.out"/>
                <delay_constant max="45e-12" in_port="ff.Q" out_port="ble6.out"/>
              </mux>
            </interconnect>
          </pb_type>
          <interconnect>
            <direct name="direct1" input="fle.in" output="ble6.in"/>
            <direct name="direct2" input="ble6.out" output="fle.out[0:0]"/>
            <direct name="direct3" input="fle.clk" output="ble6.clk"/>
          </interconnect>
        </mode>
        <!-- ${int(K)}-LUT mode definition end -->
      </pb_type>
      <interconnect>
        <!-- We use a full crossbar to get logical equivalence at inputs of CLB 
		     The delays below come from Stratix IV. the delay through a connection block
		     input mux + the crossbar in Stratix IV is 167 ps. We already have a 72 ps 
		     delay on the connection block input mux (modeled by Ian Kuon), so the remaining
		     delay within the crossbar is 95 ps. 
		     The delays of cluster feedbacks in Stratix IV is 100 ps, when driven by a LUT.
		     Since all our outputs LUT outputs go to a BLE output, and have a delay of 
		     25 ps to do so, we subtract 25 ps from the 100 ps delay of a feedback
		     to get the part that should be marked on the crossbar.	 -->
        <complete name="crossbar" input="clb.I fle[9:0].out" output="fle[9:0].in">
          <delay_constant max="95e-12" in_port="clb.I" out_port="fle[9:0].in"/>
          <delay_constant max="75e-12" in_port="fle[9:0].out" out_port="fle[9:0].in"/>
        </complete>
        <complete name="clks" input="clb.clk" output="fle[9:0].clk">
        </complete>
        <!-- This way of specifying direct connection to clb outputs is important because this architecture uses automatic spreading of opins.  
               By grouping to output pins in this fashion, if a logic block is completely filled by 6-LUTs, 
               then the outputs those 6-LUTs take get evenly distributed across all four sides of the CLB instead of clumped on two sides (which is what happens with a more
               naive specification).
          -->
        <direct name="clbouts1" input="fle[9:0].out" output="clb.O"/>
      </interconnect>
      <!-- Every input pin is driven by 15% of the tracks in a channel, every output pin is driven by 10% of the tracks in a channel -->
      <!-- Place this general purpose logic block in any unspecified column -->
    </pb_type>
    <!-- Define general purpose logic block (CLB) ends -->
  </complexblocklist>
  <power>
    <local_interconnect C_wire="2.5e-10"/>
    <mux_transistor_size mux_transistor_size="3"/>
    <FF_size FF_size="4"/>
    <LUT_transistor_size LUT_transistor_size="4"/>
  </power>
  <clocks>
    <clock buffer_size="auto" C_wire="2.5e-10"/>
  </clocks>
</architecture>
