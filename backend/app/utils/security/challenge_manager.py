from datetime import datetime, timedelta
from typing import Union
from uuid import UUID, uuid4
from app.schemas.security_schema import ChallengeSchema


class ChallengeManager:
    """class pour gerer la logique concernant le challenge"""
    
    def __init__(self, time_to_live: int = 5):
      self.ttl_minutes: int = time_to_live
      self._challenges: dict[UUID, ChallengeSchema] = {}


    def create_challenge(self) -> ChallengeSchema:
      """function pour generer un challenge"""
      
      challenge = ChallengeSchema(
        challenge_id=uuid4(),
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(minutes=self.ttl_minutes),
        used=False
      )
      
      self._challenges[challenge.challenge_id] = challenge

      return challenge
    

    def get_challenge(self, challenge_id: UUID) -> Union[ChallengeSchema, None]:
      """funct pr lire un challenge"""

      challenge = self._challenges.get(challenge_id)
      return challenge
    

    
    def is_valid(self, challenge_id: UUID) -> bool:
      """funct pr verifier si le challenge est tjrs valide"""

      challenge = self.get_challenge(challenge_id)
      
      if not challenge or challenge.used:
        return False
      
      if challenge.expires_at < datetime.now():
        return False
      
      return True
    


    def mark_challenge_as_used(self, challenge_id: UUID) -> None:
      """funct pr marquer un challenge comme deja utiliser"""

      challenge = self.get_challenge(challenge_id)

      if challenge:
        challenge.used = True

      return None