import os
os.environ["HF_TOKEN"]="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"
from utils import WebScraper, preprocess_text, parse_filtered_text
from vllm import LLM
from vllm.sampling_params import SamplingParams
import inferless
from pydantic import BaseModel, Field
from typing import Optional


@inferless.request
class RequestObjects(BaseModel):
        url: str = Field(default="https://www.producthunt.com/p/general/how-many-hours-do-you-think-a-workweek-should-have-and-what-s-the-answer-from-big-companies")
        temperature: Optional[float] = 0.15
        top_p: Optional[float] = 1.0
        repetition_penalty: Optional[float] = 1.0
        top_k: Optional[int] = -1
        max_tokens: Optional[int] = 1024
        seed: Optional[int] = 4424234

@inferless.response
class ResponseObjects(BaseModel):
        generated_result: str = Field(default='Test output')

class InferlessPythonModel:
    def initialize(self):
        model_id = "mistralai/Mistral-Small-24B-Instruct-2501"
        self.llm = LLM(model=model_id, tokenizer_mode="mistral")
        self.web_scrap_obj = WebScraper()

    def infer(self, request: RequestObjects) -> ResponseObjects:
        raw_text = self.web_scrap_obj.extract_content(request.url)
        filtered_text = preprocess_text(raw_text)
        parsed_text = [parse_filtered_text(lines) for lines in filtered_text]
        
        prompt = f"""
        You are a helpful assistant. Please read the following conversation text:
        {str(parsed_text)}
        
        Then, produce a concise summary following EXACTLY this format and style, with no deviations:
        
        What is it about?
        [Brief paragraph summarizing what the conversation discusses overall]
        
        Insights
        - **[Category/Theme 1]**:
          - [Specific point with detail]
          - [Specific point with detail]
          - [Specific point with detail]
        - **[Category/Theme 2]**:
          - [Specific point with detail]
          - [Specific point with detail]
          - [Specific point with detail]
        - **[Category/Theme 3]**:
          - [Specific point with detail]
          - [Specific point with detail]
          - [Specific point with detail]
        - **[Category/Theme 4]**:
          - [Specific point with detail]
          - [Specific point with detail]
          - [Specific point with detail]
        
        IMPORTANT FORMATTING RULES:
        1. Use exactly the format shown above
        2. Start each insight with a dash followed by bold category name and colon
        3. Use two spaces of indentation for each specific point
        4. Each specific point should start with a dash
        5. Do not add sub-categories or nested bullet points beyond what's shown in the template
        6. Avoid using author names
        6. Keep to 4-5 main categories maximum
        7. Format must match the example exactly
        
        Example of correct formatting:
        
        What is it about?
        The conversation discusses the use of AI-generated comments on social media platforms, exploring the benefits, drawbacks, and ethical implications. Participants share their opinions on whether AI comments enhance or detract from genuine social interaction.
        
        Insights
        - **Benefits of AI Comments**:
          - AI can help with grammar correction and generating basic ideas.
          - Useful for big creators to interact with fans faster and on a large scale.
          - Can assist in moderation, filtering spam, and bridging language barriers.
        - **Drawbacks of AI Comments**:
          - Lack of authenticity and personal touch.
          - Can make interactions feel artificial and insincere.
          - Risk of manipulation, bias, and creating echo chambers.
          - May lead to a loss of genuine human connection and engagement.
        - **Ethical Considerations**:
          - AI should assist rather than replace human interaction.
          - Over-reliance on AI comments can devalue the content and the effort put into creating it.
          - Users prefer genuine, human-generated responses over AI-generated ones.
        - **User Experiences**:
          - Some users find AI comments annoying and insincere.
          - Others see potential in using AI for brainstorming and generating basic content ideas.
          - There is a preference for a synergy between human and AI interaction, where AI assists but does not replace human input.
        """
        
        SYSTEM_PROMPT = (
            """You are a conversational agent that provides highly structured, well-organized responses.
            Always use proper markdown formatting with hierarchical organization.
            Group related points under thematic categories with bold headers.
            Provide comprehensive analysis rather than superficial observations.
            Maintain consistent formatting throughout your response."""
        )
        
        messages = [{
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
                   ]
        sampling_params = SamplingParams(temperature=request.temperature,top_p=request.top_p,
                                         repetition_penalty=request.repetition_penalty,
                                         top_k=request.top_k,max_tokens=request.max_tokens,seed=request.seed)
        outputs = llm.chat(messages, sampling_params=sampling_params)
        generateObject = ResponseObjects(generated_result = outputs[0].outputs[0].text)        
        return generateObject

    def finalize(self):
        self.llm = None
        self.web_scrap_obj.clear_session()
