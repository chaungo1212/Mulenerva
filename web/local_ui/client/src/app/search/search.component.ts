/* This file was created by Patrick Shane McClintock in April 2018 for the Mulenerva Project. */

import { Component, OnInit } from '@angular/core';

import { QueryService } from '../query.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit {

  query: string;
  placeholder: string = "Search For A Topic!";
  subject: string = "Select Subject";
  filter: [boolean] = [true, true, true, true];
  document_selected: boolean = false;
  video_selected: boolean = false;
  available_selected: boolean = false;
  requested_selected: boolean = false;

  Subjects = ['Art', 'Biology', 'Chemistry', 'Computer Science', 'Engineering', 'English',
    'Geology', 'History', 'Mathematics', 'Physics', 'Spanish'];

  constructor(private qs: QueryService) { }

  ngOnInit() {
  }

  updateQuery(): void {
    this.query = (<HTMLInputElement>document.getElementById('searchbar')).value;
    this.qs.setQuery(this.query);
  }

  updateSubject(): void {
    this.subject = (<HTMLInputElement>document.getElementById('subject-dropdown')).value;
    this.qs.setSubject(this.subject);
  }

  updateFilter(id: number): void {
    if (!this.filter[id]) {
      this.filter[id] = true;
    }
    else {
      this.filter[id] = false;
    }
    if (id === 0) this.document_selected = !this.filter[id];
    if (id === 1) this.video_selected = !this.filter[id];
    if (id === 2) this.requested_selected = !this.filter[id];
    if (id === 3) this.available_selected = !this.filter[id];

    this.qs.setFilter(this.filter);
    console.log(this.filter);
  }

}
