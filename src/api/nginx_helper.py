from nginxparser import dump, load


class NginxHelper:

    config_file_name = None

    def __init__(self):
        self.config_file_name = "/app/nginx/nginx.conf"

    def get_config(self):
        with open(self.config_file_name) as file:
            config = load(file)
            return config

    def add_application(self, application_name, port):
        # Parse the configuration file, append the RTMP section and write it.
        parsed_file = self.get_config()
        parsed_file.pop(3)
        rtmp_section = [['rtmp'], [[['server'], [['listen', str(port)], ['chunk_size', '8192'],
                        [['application', application_name], [['live', 'on'], ['record', 'off']]]]]]]
        if rtmp_section not in parsed_file:
            parsed_file.append(rtmp_section)
            with open(self.config_file_name, 'w') as file:
                dump(parsed_file, file)
