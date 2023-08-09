import pygsheets
from pygsheets.client import Client
from typing import List, Union

class GoogleTable:
  def __init__(
      self, credence_service_file: str = "", googlesheet_file_url: str = ""
    ) -> None:
      self.credence_service_file: str = credence_service_file
      self.googlesheet_file_url: str = googlesheet_file_url

  def _get_googlesheet_by_url(
      self, googlesheet_client: pygsheets.client.Client
    ) -> pygsheets.Spreadsheet:
      sheets: pygsheets.Spreadsheet = googlesheet_client.open_by_url(
          self.googlesheet_file_url
        )
      return sheets.sheet1

  def _get_googlesheet_client(self) -> Client:
    return pygsheets.authorize(
          service_file=self.credence_service_file
        )

  def search_user(
      self,
      data: Union[str, List[str]],
      name_col: int = 1,
      surname_col: int = 2,
      post_col: int = 3,
      tg_col: int = 4,
      phone_num_col: int = 5,
      email_col: int = 6,
      birth_date_col: int = 7,
    ) -> List[dict]:
      googlesheet_client: pygsheets.client.Client = self._get_googlesheet_client()
      wks: pygsheets.Spreadsheet = self._get_googlesheet_by_url(googlesheet_client)

      find_cells = wks.find(data, cols=(name_col, birth_date_col), includeFormulas=True)

      if not find_cells:
        return []

      results = []
      for cell in find_cells:
        row = cell.row
        name = wks.get_value((row, name_col))
        surname = wks.get_value((row, surname_col))
        post = wks.get_value((row, post_col))
        email = wks.get_value((row, email_col))
        birth_date = wks.get_value((row, birth_date_col))
        tg = wks.get_value((row, tg_col))
        phone_num = wks.get_value((row, phone_num_col))
        results.append({
              'name': name,
              'surname': surname,
              'post': post,
              'email': email,
              'birth_date': birth_date,
              'tg': tg,
              'phone_num': phone_num
            })

      return results
