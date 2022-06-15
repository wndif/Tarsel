import os
import numpy as np

if __name__ == "__main__":
    Case = "lshift_reg/lshift_reg_wadden_buggy2/"
    versions = os.listdir(os.path.join(Case, "extract"))
    for version in versions:
        wpath = os.path.join("Coverage_Info", Case, version)
        if not os.path.exists(wpath):
            os.makedirs(wpath)

        infos_path = os.path.join(Case, "extract", version)
        infos_files = os.listdir(infos_path)
        statement_dict = {}
        dict_sum = 0
        coverage_matrix = []
        infos_files.sort(key=lambda x:int(x[7:-4]))
        for info in infos_files:
            #print(info[7:-4])
            print(version, info)
            if "extract" not in info:
                continue
            info_path = os.path.join(Case, "extract", version, info)
            with open(info_path, 'r') as info_file:
                statements = info_file.readlines()
                # print(len(statements))
                coverage = [0 for i in range(len(statements))]
                for statement in statements:
                    s, count = statement.split(" ")
                    count = eval(count)
                    #print(f'{s} ---  {count}')
                    if s not in statement_dict:
                        statement_dict[s] = dict_sum
                        statement_num = dict_sum
                        dict_sum += 1
                    else:
                        statement_num = statement_dict[s]
                    if count > 0:
                        coverage[statement_num] = 1
                coverage_matrix.append(coverage)
            #break
        coverage_matrix = np.array(coverage_matrix)
        print(coverage_matrix.shape)
        np.savetxt(os.path.join("Coverage_Info", Case, version, "covMatrix.txt"), coverage_matrix, fmt='%d')

        componentinfo = ""
        componentinfo += str(len(statement_dict)) + "\n"
        componentlabel = componentinfo
        for key, value in statement_dict.items():
            componentlabel += str(value) + ":" + key + "\n"
            componentinfo += str(value) + " "
        with open(os.path.join("Coverage_Info", Case, version, "componentinfo.txt"), 'w') as f:
            f.write(componentinfo)
        with open(os.path.join("Coverage_Info", Case, version, "componentlabel.txt"), 'w') as f:
            f.write(componentlabel)
        
# =============================================================================
#         error = [0 for i in infos_files]
#         with open(os.path.join(Case, "result", version+".txt"), 'r') as f:
#             error_str = f.readlines()
#             error_str = [int(e) for e in error_str]
#             for ei in error_str:
#                 error[ei] = 1
#         np.savetxt(os.path.join("Coverage_Info", Case, version, "error.txt"), error, fmt='%d', delimiter='\n')
# =============================================================================
                