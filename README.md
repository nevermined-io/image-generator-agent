[![banner](https://raw.githubusercontent.com/nevermined-io/assets/main/images/logo/banner_logo.png)](https://nevermined.io)

Image Generator Agent using Nevermined's Payments API (Python)
==============================================================

> A **Python-based agent** that generates realistic, high-quality images of characters using **Stable Diffusion** and custom prompts. Seamlessly integrated with **Nevermined's Payments API**, this agent efficiently handles task requests and billing.

* * *

Table of Contents
-----------------

1.  [Introduction](#introduction)
2.  [Getting Started](#getting-started)
    *   [Installation](#installation)
    *   [Running the Agent](#running-the-agent)
3.  [Project Structure](#project-structure)
4.  [Integration with Nevermined Payments API](#integration-with-nevermined-payments-api)
5.  [How to Create Your Own Agent](#how-to-create-your-own-agent)
    *   [1. Subscribing to Task Requests](#1-subscribing-to-task-requests)
    *   [2. Handling Task Lifecycle](#2-handling-task-lifecycle)
    *   [3. Generating Images with Stable Diffusion](#3-generating-images-with-stable-diffusion)
    *   [4. Validating Steps and Sending Logs](#4-validating-steps-and-sending-logs)
6.  [Model Download](#model-download)
7.  [License](#license)

* * *

Introduction
------------

The **Image Generator Agent** is an application designed to produce high-quality character images based on detailed prompts. Using **Stable Diffusion**, it transforms textual character descriptions into stunning visuals.

This agent works within the **Nevermined ecosystem**, utilizing the **Payments API** for:

*   **Task management**: Process task requests and return results.
*   **Billing integration**: Ensure tasks align with the allocated budget.
*   **Event-driven architecture**: Automatically process events without a dedicated server.

This agent typically operates after the **Character Extraction Agent**, taking character descriptions as input, generating corresponding images, and uploading them to IPFS for distribution.

* * *

Getting Started
---------------

### Installation

1.  **Clone the repository**:
    
    ```bash
    git clone https://github.com/nevermined-io/image-generator-agent.git
    cd image-generator-agent
    ```
    
2.  **Set up a virtual environment** (optional but recommended):
    
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    
3.  **Install dependencies**:
    
    ```bash
    pip install -r requirements.txt
    ```
    
4.  **Configure environment variables**:
    
    *   Copy the `.env.example` file to `.env`:
        
        ```bash
        cp .env.example .env
        ```
        
    *   Populate the `.env` file with the following details:
        
        ```bash
        NVM_API_KEY=YOUR_NVM_API_KEY
        PINATA_API_KEY=YOUR_PINATA_API_KEY
        PINATA_API_SECRET=YOUR_PINATA_API_SECRET
        NVM_ENVIRONMENT=testing  # or staging/production
        AGENT_DID=YOUR_AGENT_DID
        ```
        
5.  **Download the model**:
    
    *   Download the `analog-madness` model from [CivitAI](https://civitai.com/models/8030/analog-madness-realistic-model) in **safetensor (fp16)** format.
    *   Place the file in the `models` directory:
        
        ```plaintext
        models/
        └── analogMadness_v70.safetensors
        ```
        

* * *

### Running the Agent

Run the agent with the following command:

```bash
python main.py
```

The agent will subscribe to the Nevermined task system and begin processing image generation requests.

* * *

Project Structure
-----------------

```plaintext
image-generator-agent/
├── src/
│   ├── main.py                # Main entry point for the agent
│   ├── image_generator.py     # Image generation logic using Stable Diffusion
│   ├── utils/
│       └── utils.py           # Utility functions for IPFS uploads
├── models/                    # Directory for the Stable Diffusion model
├── .env.example               # Example environment variables file
├── requirements.txt           # Python dependencies
├── .gitignore                 # Files and directories to ignore
```

### Key Components:

1.  **`main.py`**: Handles task requests, image generation, and task updates.
2.  **`image_generator.py`**: Contains the logic for generating images using Stable Diffusion.
3.  **`utils/utils.py`**: Includes helper functions, like uploading images to IPFS.

* * *

Integration with Nevermined Payments API
----------------------------------------

The **Nevermined Payments API** is central to this agent’s functionality, providing tools for task management, billing, and event subscription.

1.  **Initialize the Payments Instance**:
    
    ```python
    from payments_py import Payments, Environment
    
    payment = Payments(
        app_id="image_generator_agent",
        nvm_api_key=nvm_api_key,
        version="1.0.0",
        environment=Environment.get_environment(environment),
        ai_protocol=True,
    )
    ```
    
2.  **Subscribe to Task Updates**:
    
    ```python
    await payment.ai_protocol.subscribe(
        agent.run,
        join_account_room=False,
        join_agent_rooms=[agent_did],
        get_pending_events_on_subscribe=False
    )
    ```
    
3.  **Task Lifecycle**:
    
    *   Fetch step details:
        
        ```python
        step = payment.ai_protocol.get_step(step_id)
        ```
        
    *   Update step status:
        
        ```python
        payment.ai_protocol.update_step(
            did=step['did'],
            task_id=step['task_id'],
            step_id=step['step_id'],
            step={
                'step_status': 'Completed',
                'output_artifacts': [image_url],
            },
        )
        ```
        

For detailed integration steps, refer to the [official documentation](https://docs.nevermined.app/docs/tutorials/integration/agent-integration).

* * *

How to Create Your Own Agent
----------------------------

### 1\. Subscribing to Task Requests

Task requests are handled by subscribing to the Nevermined Payments API. The `subscribe` method listens for incoming tasks and processes them using the `run` function:

```python
await payment.ai_protocol.subscribe(
    agent.run,
    join_account_room=False,
    join_agent_rooms=[agent_did],
    get_pending_events_on_subscribe=False
)
```

* * *

### 2\. Handling Task Lifecycle

The `run` function processes incoming tasks:

```python
async def run(data):
    step = self.payment.ai_protocol.get_step(data['step_id'])
    if step['step_status'] != 'Pending':
        return

    character = step.get('input_query', '')
    image = self.image_generator.generate_image(character)
    image_url = upload_image_and_get_url(image)

    self.payment.ai_protocol.update_step(
        did=step['did'],
        task_id=step["task_id"],
        step_id=step['step_id'],
        step={
            'step_status': 'Completed',
            'output_artifacts': [image_url],
        }
    )
```

* * *

### 3\. Generating Images with Stable Diffusion

The `image_generator.py` handles image creation:

```python
from diffusers import StableDiffusionPipeline
import torch

class ImageGenerator:
    def generate_image(self, character):
        prompt = f"photo of {character} (cinematic lighting:1.1) ..."
        return self.pipe(prompt).images[0]
```

* * *

### 4\. Validating Steps and Sending Logs

Logs track task progress and errors:

```python
from payments_py.data_models import TaskLog

await self.payment.ai_protocol.log_task(TaskLog(
    task_id=step['task_id'],
    message='Image generated successfully.',
    level='info',
    task_status='Completed'
))
```

* * *

Model Download
--------------

The **analog-madness** model is used for image generation. Download it from [CivitAI](https://civitai.com/models/8030/analog-madness-realistic-model) in **safetensor (fp16)** format and place it in the `models` directory.

```plaintext
models/
└── analogMadness_v70.safetensors
```

* * *

License
-------

```
Copyright 2024 Nevermined AG

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```