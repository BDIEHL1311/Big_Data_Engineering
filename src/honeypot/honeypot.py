import json
import random
import time
from datetime import datetime
from confluent_kafka import Producer
from config.base_config import BaseConfig, setup_logging

logger = setup_logging('honeypot')
config = BaseConfig()

class HoneypotSimulator:
    COUNTRIES = ['Germany', 'China', 'Russia', 'USA', 'Brazil', 'India']
    USERNAMES = ['admin', 'root', 'user', 'test', 'oracle', 'mysql', 'postgres']
    PASSWORDS = ['123456', 'password', 'admin', 'root123', 'qwerty', '111111']
    IP_RANGES = {
        'Germany': '91.0.0.0/24',
        'China': '114.0.0.0/24',
        'Russia': '95.0.0.0/24',
        'USA': '104.0.0.0/24',
        'Brazil': '177.0.0.0/24',
        'India': '115.0.0.0/24'
    }
    
    def __init__(self):
        self.producer = self._create_producer()
    
    def _create_producer(self):
        conf = {
            'bootstrap.servers': config.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'ssh-honeypot-producer'
        }
        return Producer(conf)
    
    def generate_ip(self, network: str) -> str:
        base_ip = network.split('/')[0]
        base_parts = [int(x) for x in base_ip.split('.')]
        return f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{random.randint(0,255)}"
    
    def generate_log_entry(self):
        country = random.choice(self.COUNTRIES)
        current_time = datetime.now()
        
        return {
            "timestamp": int(current_time.timestamp()),
            "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "ip": self.generate_ip(self.IP_RANGES[country]),
            "country": country,
            "username": random.choice(self.USERNAMES),
            "password": random.choice(self.PASSWORDS),
            "success": random.random() < 0.01  # 1% success rate
        }
    
    def delivery_callback(self, err, msg):
        if err:
            logger.error('Message delivery failed', extra={'error': str(err)})
        else:
            logger.debug('Message delivered', 
                        extra={'topic': msg.topic(), 'partition': msg.partition()})
    
    def run(self):
        logger.info('Starting SSH Honeypot simulation')
        
        try:
            while True:
                try:
                    log_entry = self.generate_log_entry()
                    self.producer.produce(
                        config.KAFKA_TOPIC,
                        key=log_entry['ip'],
                        value=json.dumps(log_entry),
                        callback=self.delivery_callback
                    )
                    self.producer.poll(0)
                    
                    logger.info('Generated log entry', extra={'log_entry': log_entry})
                    time.sleep(random.uniform(0.1, 2))
                    
                except BufferError:
                    logger.warning('Producer queue is full - waiting')
                    self.producer.flush()
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error('Error in message generation', 
                               extra={'error': str(e)})
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info('Stopping honeypot simulation')
        
        finally:
            self.producer.flush(timeout=5)
            self.producer.close()

if __name__ == "__main__":
    simulator = HoneypotSimulator()
    simulator.run()