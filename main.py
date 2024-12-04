# main.py

import json
from dotenv import load_dotenv
import os
import asyncio
from payments_py import Environment, Payments
from payments_py.data_models import AgentExecutionStatus, TaskLog
from image_generator import ImageGenerator
from utils.utils import upload_image_and_get_url

load_dotenv()

# Retrieve API keys and environment variables from the system environment
nvm_api_key = os.getenv('NVM_API_KEY')
environment = os.getenv('NVM_ENVIRONMENT')
agent_did = os.getenv('AGENT_DID')

class ImageGeneratorAgent:
    """
    An agent that uses the ImageGenerator class and Nevermined's Payments API to generate images.
    """

    def __init__(self, payment, image_generator):
        """
        Initialize the ImageGeneratorAgent with a Payments instance and an ImageGenerator instance.

        Args:
            payment (Payments): The Payments instance for interacting with Nevermined's API.
            image_generator (ImageGenerator): The ImageGenerator instance for generating images.
        """
        self.payment = payment
        self.image_generator = image_generator

    async def run(self, data):
        """
        Process incoming data to generate images and update task status via Nevermined's API.

        Args:
            data (dict): A dictionary containing task and step information.

        Returns:
            None
        """

        # Retrieve the current step information using the step_id from data
        step = self.payment.ai_protocol.get_step(data['step_id'])

        # Check if the step status is pending; if not, exit the function
        if step['step_status'] != AgentExecutionStatus.Pending.value:
            print('Step status is not pending')
            return

        # Log the initiation of the image generation task
        await self.payment.ai_protocol.log_task(TaskLog(
            task_id=step['task_id'],
            message='Starting image generation...',
            level='info'
        ))

        # Extract the character object from input_query
        input_query = step.get('input_query', '')
        

        #tcheck if character prompt is a string with json format. If so, convert it to a dictionary
        if isinstance(input_query, str) and input_query.startswith('{') and input_query.endswith('}'):
            try:
                character_prompt_dict = json.loads(input_query)
                # convert the dictionary to a string with key value pairs separated by new lines
                character_prompt = '\n'.join([f"{k}: {v}" for k, v in character_prompt_dict.items()])

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                character_prompt = None
        else:
            character_prompt = input_query

        print("Character Prompt:", character_prompt)

        if not character_prompt:
            print("No character data provided")
            await self.payment.ai_protocol.log_task(TaskLog(
                task_id=step['task_id'],
                message='No character data provided.',
                level='error',
                task_status=AgentExecutionStatus.Failed.value
            ))
            return

        try:
            # Use the ImageGenerator instance to generate the image
            image = self.image_generator.generate_image(character_prompt)
            
            # Upload the image to IPFS and get the public URL
            ipfs_url = upload_image_and_get_url(image, filename=f"{data['task_id']}.png")
            print("IPFS URL:", ipfs_url)

            # Update the task step with the image data and mark it as completed
            self.payment.ai_protocol.update_step(
                did=data['did'],
                task_id=data['task_id'],
                step_id=data['step_id'],
                step={
                    'step_id': data['step_id'],
                    'task_id': data["task_id"],
                    'step_status': AgentExecutionStatus.Completed.value,
                    'output': 'Image generated and uploaded to IPFS',
                    'is_last': True,
                    'output_artifacts': [ipfs_url],
                },
            )

            # Log the completion of the image generation task
            await self.payment.ai_protocol.log_task(TaskLog(
                task_id=step['task_id'],
                message='Image generation and upload to IPFS completed.',
                level='info',
                task_status=AgentExecutionStatus.Completed.value
            ))

        except Exception as e:
            # Handle any exceptions that occur during the image generation process
            print("Error during image generation:", e)
            # Log the error and update the task status to 'Failed'
            await self.payment.ai_protocol.log_task(TaskLog(
                task_id=step['task_id'],
                message=f'Error during image generation: {e}',
                level='error',
                task_status=AgentExecutionStatus.Failed.value
            ))
            return

async def main():
    """
    The main function that initializes the Payments object, creates the ImageGeneratorAgent,
    and subscribes to Nevermined's AI protocol to listen for incoming image generation tasks.

    Returns:
        None
    """
    # Initialize the Payments object with the necessary configurations
    payment = Payments(
        app_id="image_generator_agent",
        nvm_api_key=nvm_api_key,
        version="1.0.0",
        environment=Environment.get_environment(environment),
        ai_protocol=True,
    )

    # Create an instance of the ImageGenerator class
    image_generator = ImageGenerator()

    # Create an instance of the ImageGeneratorAgent with the Payments object and ImageGenerator
    agent = ImageGeneratorAgent(payment, image_generator)

    # Subscribe to the AI protocol to receive tasks assigned to this agent
    subscription_task = asyncio.get_event_loop().create_task(
        payment.ai_protocol.subscribe(
            agent.run,
            join_account_room=False,
            join_agent_rooms=[agent_did],
            get_pending_events_on_subscribe=False
        )
    )

    try:
        # Await the subscription task to keep the agent running
        await subscription_task
    except asyncio.CancelledError:
        # Handle the cancellation of the subscription task gracefully
        print("Subscription task was cancelled")

if __name__ == '__main__':
    # Run the main function using asyncio's event loop
    import torch
    asyncio.run(main())
