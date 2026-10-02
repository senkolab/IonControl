import matlab.engine

# Start the MATLAB engine for Python
eng = matlab.engine.start_matlab()

# Call a MATLAB function
result = eng.SendAWGCommand("OUTP:STAT 0")

# Print the result
print(result)

# Stop the MATLAB engine for Python
eng.quit()
