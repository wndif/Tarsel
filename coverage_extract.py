import os
import shutil


if __name__ == "__main__":
    origin_path = "opencores/i2c/i2c_master_bit_ctrl_kgoliya_buggy1/report"
    target_path = "opencores/i2c/i2c_master_bit_ctrl_kgoliya_buggy1/extract"


    bugdirs = os.listdir(origin_path)
    for bugdir in bugdirs:
        if not os.path.exists(os.path.join(target_path, bugdir)):
            os.makedirs(os.path.join(target_path, bugdir))
        files = os.listdir(os.path.join(origin_path, bugdir))
        for fi in files:
            file_name = ""
            file_dict = {}
            filename_flag = True
            statement_start = 0
            branch_start = 0
            branch_end = 0
            statement_start_flag = True
            branch_start_flag= True
            branch_end_flag = True
            if "report" not in fi:
                shutil.copy(os.path.join(origin_path, bugdir, fi), os.path.join(target_path, bugdir, fi))
                continue
            origin_fname = os.path.join(origin_path, bugdir, fi)
            target_fname = os.path.join(target_path, bugdir, fi.replace("report", "extract"))

            with open(origin_fname, 'r') as f:
                lines = f.readlines()
                #(lines[0])
                wr_str = ""
                for i in range (0,len(lines)):
                    if "Statement Details" in lines[i] and statement_start_flag == True:
                        statement_start = i
                        statement_start_flag = False
                    if "Branch Details" in lines[i] and branch_start_flag == True:
                        branch_start = i
                        branch_start_flag = False
                    if ("Condition Coverage" in lines[i] or "Statement Coverage" in lines[i]) and branch_end_flag == True:
                        branch_end = i - 2
                        branch_end_flag = False
                    if "File:" in lines[i] and filename_flag == True:
                        file_dict = {}
                        index_l = lines[i].find("Workspace") + 11
                        index_r = lines[i].find(".v") + 2
                        file_name = lines[i][index_l:index_r]
                        #print(file_name)
                        filename_flag = False
                        
                #statements extract;     
                for i in range (statement_start+4,len(lines)):
                    #print(lines[i],"\n")                   
                    if lines[i] == "\n":
                        break
                    else:
                        line_number = eval(lines[i][0:10])
                        cover_type_str = lines[i][10:30]
                        exec_count_str = lines[i][30:50]
                        exec_count = 0
                        try:
                            cover_type = eval(cover_type_str)
                            if "***0***" in exec_count_str:
                               exec_count = 0
                            else:
                                exec_count = eval(exec_count_str)
                            #print(line_number, cover_type, exec_count)
                            statement = str(line_number) + "-" + str(cover_type)
                            file_dict[statement] = exec_count
                        except SyntaxError:
                            pass
                    
                #branches extract; 
                for i in range (branch_start+1, branch_end):
                    #print(lines[i])
                #break
                    if "CASE Branch" in lines[i]:
                        continue
                    if "IF Branch" in lines[i]:
                        continue
                    if "Branch totals" in lines[i]:
                        continue
                        #if "Branch totals" not in s:
                    if "All False Count" in lines[i]: 
                        continue
                    if "Branch Coverage" in lines[i]: 
                        continue
                    if lines[i] == "\n":
                        continue
                    #print(lines[i])
                    else:
                        line_number = eval(lines[i][0:10])
                        cover_type_str = lines[i][10:30]
                        exec_count_str = lines[i][30:50]
                        exec_count = 0
                        try:
                            cover_type = eval(cover_type_str)
                            if "***0***" in exec_count_str:
                                exec_count = 0
                            else:
                                exec_count = eval(exec_count_str)
                            print(line_number, cover_type, exec_count)
                            statement = str(line_number) + "-" + str(cover_type)
                            file_dict[statement] = exec_count
                        except SyntaxError:
                            pass
                for key, value in file_dict.items():
                    wr_str += file_name[:-2] + "-" + key + " " + str(value) + "\n"
                f2 = open(target_fname, 'w')
                f2.write(wr_str)
                f2.close()