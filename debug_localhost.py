import re

def debug_localhost_parsing():
    command_str = "localhost && tasklist"
    
    print(f"Original command: '{command_str}'")
    
    # &, ;, |, && で分割
    commands = re.split(r'\s*[;&|]+\s*', command_str)
    print(f"Split commands: {commands}")
    
    for i, cmd_part in enumerate(commands):
        cmd_part = cmd_part.strip()
        print(f"\nProcessing part {i}: '{cmd_part}'")
        print(f"Length: {len(cmd_part)}")
        print(f"cmd_part.lower(): '{cmd_part.lower()}'")
        print(f"cmd_part.lower() == 'localhost': {cmd_part.lower() == 'localhost'}")
        
        if cmd_part.lower() == 'localhost':
            print("✅ localhost recognized and would be skipped")
        else:
            words = cmd_part.split()
            if words:
                first_word = words[0]
                cmd_name = first_word.lower()
                print(f"First word: '{first_word}', cmd_name: '{cmd_name}'")

if __name__ == "__main__":
    debug_localhost_parsing()