from typing import Dict, List, Optional, Union


def generate_section_model(
    title: str = "Test Title", text="Lorum ipsum", media: Optional[List[Dict]] = None
) -> Dict[str, Union[str, Optional[List[Dict]]]]:
    return dict(title=title, text=text, media=media)
