import spade
import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template

class RobotAgent(Agent):
    class PickupBehavior(OneShotBehaviour):
        async def run(self):
            print("Robot sedang memungut sampah...")
            user_input = input("Masukkan jumlah sampah yang terkumpul (dalam kilogram): ")
            if user_input == "10":
                msg = Message(to="agentbin@localhost")
                msg.set_metadata("performative", "inform")
                msg.body = "Sampah seberat 10 kg akan segera dikirim ke tempat sampah."

                await self.send(msg)
                print("Pesan terkirim ke tempat sampah pintar!")
            else:
                print(f"Jumlah sampah {user_input} kg belum mencukupi untuk dikirim.")

            await self.agent.stop()

    async def setup(self):
        print("Robot Agent started")
        b = self.PickupBehavior()
        self.add_behaviour(b)

class SmartBinAgent(Agent):
    class ReceiveBehavior(OneShotBehaviour):
        async def run(self):
            print("Tempat sampah pintar siap menerima sampah...")

            msg = await self.receive(timeout=15)
            if msg:
                print("Pesan diterima:", msg.body)
                
                # Memulai proses pemilahan sampah
                print("Memulai memilah sampah-sampah...")
                for i in range(10):
                    print(f"Memilah sampah... ({i+1}/10) detik")
                    time.sleep(1)
                print("Pemilahan sampah selesai!")
                
                # Mengirim pesan ke HumanAgent setelah menerima pesan dari RobotAgent dan memilah sampah
                msg_to_human = Message(to="agentcleaner@localhost")
                msg_to_human.set_metadata("performative", "inform")
                msg_to_human.body = "Sampah sudah dipilah, segera ambil!"
                await self.send(msg_to_human)
                print("Pesan terkirim ke Human Agent!")
            else:
                print("Tidak ada sampah yang dikirim dalam 15 detik terakhir.")

            await self.agent.stop()

    async def setup(self):
        print("Tempat Sampah Pintar started")
        b = self.ReceiveBehavior()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)

class HumanAgent(Agent):
    class ReceiveBehavior(OneShotBehaviour):
        async def run(self):
            print("Human Agent siap menerima pesan...")

            msg = await self.receive(timeout=30)
            if msg:
                print("Pesan diterima:", msg.body)
            else:
                print("Tidak ada pesan yang diterima dalam 30 detik terakhir.")

            await self.agent.stop()

    async def setup(self):
        print("Human Agent started")
        b = self.ReceiveBehavior()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)

async def main():
    human_agent = HumanAgent("agentcleaner@localhost", "12345")
    await human_agent.start(auto_register=True)
    print("Human Agent started")

    smart_bin_agent = SmartBinAgent("agentbin@localhost", "12345")
    await smart_bin_agent.start(auto_register=True)
    print("Tempat Sampah Pintar started")

    robot_agent = RobotAgent("agentrobot@localhost", "12345")
    await robot_agent.start(auto_register=True)
    print("Robot Agent started")

    await spade.wait_until_finished(smart_bin_agent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main())
