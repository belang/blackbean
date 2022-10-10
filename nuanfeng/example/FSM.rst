Module - control
================

There are three states in Control.

.. table:: FSM - fsm_control

   =======  ===========
   state    discription
   =======  ===========
   IDLE     initial value or reset value
   RUN      the core are running
   HOLD     hold on current state
   STOP     the core stop
   =======  ===========


The states transfer condition is:

.. table:: FSM_TRAN - fsm_control


   ===========  ==========  =========
   state        next_state  condition
   ===========  ==========  =========
   ANY          IDLE        RESET
   IDLE         RUN         
   RUN          STOP        !i_valid
   RUN          HOLD        i_hold
   STOP         RUN         i_valid
   HOLD         STOP        !i_valid
   HOLD         RUN         !i_hold
   ===========  ==========  =========

.. table:: IO - interface

   ==========  ===  ======  ==============  ===========
   name        dir  width   data            discription
   ==========  ===  ======  ==============  ===========
   i_valid     i    1                       enable module to run
   o_state     o    2       fsm_control_cs  export current state
   ==========  ===  ======  ==============  ===========
