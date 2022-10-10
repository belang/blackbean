// author: lianghy
// time: 9/9/2022 10:44:48 AM


module a
    (
    input wire  clk,
    input logic rst_n,
    );

//====================
// resource
//====================

typedef enum logic[15:0]
{
    REG = 16'h0000
} my_dest_t;

typedef enum logic [:0] {} ;

always @(/* sensitive list */) begin
    
end

always_ff @(posedge clk or negedge rst_n) begin : name
    if (!rst_n) begin
        name_cs <= x;
    end else begin
        name_cs <= name_ns;
    end
end : name

always_comb begin : name_transfer
    unique case (name_cs)
        state: begin
            if (valid) begin
                name_ns = state;
            end
        end
        state: begin
            if (valid) begin
                name_ns = state;
            end
        end
        default: begin
            name_ns = name_cs;
        end
    endcase
end : name_transfer
endmodule
