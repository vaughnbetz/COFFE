*** INCLUDE ALL LIBRARIES

.LIB INCLUDES

* Include process data (voltage levels, gate length and device models library)
.LIB "process_data.l" PROCESS_DATA

* Include transistor parameters
* Include wire resistance and capacitance
* Include basic subcircuits
.LIB "basic_subcircuits.l" BASIC_SUBCIRCUITS

* Include subcircuits
.LIB "subcircuits.l" SUBCIRCUITS

* Include sweep data file for .DATA sweep analysis
.INCLUDE "sweep_data.l"

.ENDL INCLUDES