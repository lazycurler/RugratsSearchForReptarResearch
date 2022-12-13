local rngAddr=0x000c3f94
local rng
local rng_old=0
local rng_count=-1

function main()
  console.clear()

  event.onloadstate(on_load_state)

  while true do
    rng=mainmemory.read_s32_le(rngAddr)
  
    if(rng_old ~= rng)
    then
      rng_count = rng_count + 1
      rng_old = rng
    end
  
    gui.text(5,10,"Relative RNG Frame Change Count: " .. string.format(rng_count))
    gui.text(5,30,"                      RNG Value: 0x" .. string.format("%02X", rng))
  
    emu.frameadvance()
  end
end


function on_load_state()
  rng_count = -1
end

main()