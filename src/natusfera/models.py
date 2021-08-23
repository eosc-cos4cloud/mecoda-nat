from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum, IntEnum


# Objetos de las entidades de nuestro programa: observaciones y proyectos
class Project(BaseModel):
    id: int
    title: str
    description: Optional[str] = None    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    place_id: Optional[int] = None
    parent_id: Optional[int] = None
    children_id: List[int] = []
    user_id: Optional[int] = None
    icon_url: Optional[str] = None
    observed_taxa_count: Optional[int] = None

class IconicTaxon(IntEnum):
    chromista = 16
    protozoa = 14
    animalia = 2
    mollusca = 15
    arachnida = 9
    insecta = 11
    aves = 5
    mammalia = 8
    amphibia = 7
    reptilia = 6
    actinopterygii = 3
    fungi = 13
    plantae = 12

class Taxon(BaseModel):
    iconic_taxon: Optional[IconicTaxon] = None
    id: Optional[int] = None
    name: Optional[str] = None

class Photo(BaseModel):
    id: Optional[int] = None
    large_url: Optional[str] = None
    medium_url: Optional[str] = None
    small_url: Optional[str] = None

class QualityGrade(str, Enum):
    basico = 'casual'
    investigacion = 'research'

class Observation(BaseModel):
    id: int
    captive: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    observed_on: Optional[date] = None
    description: Optional[str] = None  
    iconic_taxon: Optional[IconicTaxon] = None
    taxon: Optional[Taxon] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    place_id: Optional[int] = None
    quality_grade: Optional[QualityGrade] = None 
    user_id: Optional[int] = None
    user_login: Optional[str] = None
    project_ids: List[int] = []
    photos: List[Photo] = []
    num_identification_agreements: Optional[int] = None
    num_identification_disagreements: Optional[int] = None








