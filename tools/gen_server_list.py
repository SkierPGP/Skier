"""<optgroup label="PKS/SKS Servers">
                    <option>pgp.mit.edu</option>
                </optgroup>
                <optgroup label="Skier servers">
                    <option>pgp.sundwarf.me</option>
                </optgroup>"""
import configmaster

cfg = configmaster.YAMLConfigFile.YAMLConfigFile("config.yml")
cfg.apply_defaults(configmaster.YAMLConfigFile.YAMLConfigFile("config.default.yml"))


count = 0
base = "<optgroup label=\"PKS/SKS Servers\">\n"
for server in cfg.config.sks_imports:
    print("Adding PKS/SKS server {}".format(server))
    base += "<option>{}</option>\n".format(server)
    count += 1

base += "</optgroup>\n<optgroup label=\"Skier Servers\">\n"
for server in cfg.config.skier_imports:
    print("Adding Skier server {}".format(server))
    base += "<option>{}</option>\n".format(server)
    count += 1

base += "</optgroup>\n"

print("Updated severs list with {} servers".format(count))
x = open("templates/generated/_servers.html", 'w')
x.write(base)
x.close()

