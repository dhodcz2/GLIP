import os

# Get the current directory where this __init__.py file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define file paths for each YAML file
coco_yaml_path = os.path.join(current_dir, '_coco.yaml')
glip_a_swin_t_o365_yaml_path = os.path.join(current_dir, 'glip_A_Swin_T_O365.yaml')
glip_swin_l_yaml_path = os.path.join(current_dir, 'glip_Swin_L.yaml')
glip_swin_t_o365_yaml_path = os.path.join(current_dir, 'glip_Swin_T_O365.yaml')
glip_swin_t_o365_goldg_yaml_path = os.path.join(current_dir, 'glip_Swin_T_O365_GoldG.yaml')
