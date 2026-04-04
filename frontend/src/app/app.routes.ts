import { Routes } from '@angular/router';
import { FaqDraftsListComponent } from './faq-drafts-list/faq-drafts-list.component';
import { FaqDetailComponent } from './faq-detail/faq-detail.component';
import { FaqEditComponent } from './faq-edit/faq-edit.component';
import { SupportRecordsListComponent } from './support-records-list/support-records-list.component';

export const routes: Routes = [
	{
		path: '',
		component: FaqDraftsListComponent
	},
	{
		path: 'faq-drafts/:id',
		component: FaqDetailComponent
	},
	{
		path: 'faq-drafts/:id/edit',
		component: FaqEditComponent
	},
	{
		path: 'records',
		component: SupportRecordsListComponent
	}
];
