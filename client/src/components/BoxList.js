import React, {Component} from "react";
import { connect } from 'react-redux';
import {Pagination, ListGroup, ListGroupItem, PageHeader, FormGroup, Radio} from 'react-bootstrap';
import Moment from "moment";
import { isEqual } from 'lodash';
import * as actions from "../actions";
import MyBreadcrumbs from "./MyBreadcrumbs";


const ORDERING = {
  pulls: '-pulls',
  updated: '-date_updated',
};
const DEFAULT_ORDERING = ORDERING.pulls;


class BoxList extends Component {
  componentDidMount() {
    this.fetchBoxes();
  }

  componentDidUpdate(prevProps) {
    if (!isEqual(prevProps.location.query, this.props.location.query)) {
      // For a case, when changing page or ordering.
      this.fetchBoxes();
      return;
    }

    if (prevProps.params.username !== this.props.params.username) {
      // For a case, when navigating by breadcrumb,
      // or back and forth in browser.
      this.fetchBoxes();
    }
  }

  onPageChange = (page) => {
    const location = this.props.router.createLocation({
      pathname: this.props.location.pathname,
      query: {
        order: this.props.location.query.order,
        page,
        q: this.props.location.query.q,
      }
    });
    this.props.router.push(location);
  };

  onBoxClick = (e) => {
    e.preventDefault();
    this.props.router.push(
        // Relative url
        e.currentTarget.getAttribute("href")
    );
    return false;
  };

  onBoxOrderChange = (e) => {
    const location = this.props.router.createLocation({
      pathname: this.props.location.pathname,
      query: {
        order: e.target.value,
        page: this.props.location.query.page,
        q: this.props.location.query.q,
      }
    });
    this.props.router.push(location);
  };

  fetchBoxes = () => {
    this.props.fetchBoxes(
        this.props.params.username,
        this.props.location.query.page || 1,
        ORDERING[this.props.location.query.order] || DEFAULT_ORDERING,
        this.props.location.query.q
    );
  };

  renderBoxesList = () => {
    if (!this.props.boxesPages) {
      return;
    }
    if (this.props.boxesPages.count === 0) {
      return <p>No boxes</p>
    }
    const boxesTags = this.props.boxesPages.pages[this.activePage];
    if (!boxesTags) {
      return;
    }

    return boxesTags.map(tag => {
      const box = this.props.boxes[tag];
      return (
          <ListGroupItem
              key={tag}
              href={`/boxes/${tag}`}
              onClick={this.onBoxClick}
          >
            <div>
              <h4>{tag}</h4>
              <p>{box.short_description}</p>
            </div>
            <div>
              {box.pulls} pulls
            </div>
            <small title={Moment(box.date_updated).format('LLL')}>
              Last updated: {Moment(box.date_updated).fromNow()}
            </small>
            <div className="clearfix"></div>
          </ListGroupItem>
      );
    });
  };

  renderPagination = () => {
    if (!this.props.boxesPages) {
      return;
    }
    if (this.props.boxesPages.count <= 10) {
      return;
    }

    const items = Math.ceil(this.props.boxesPages.count / 10);
    return (
        <Pagination
            prev
            next
            first
            last
            ellipsis
            boundaryLinks
            items={items}
            maxButtons={5}
            activePage={this.activePage}
            onSelect={this.onPageChange}
        />
    );
  };

  renderOrderControls = () => {
    const order = this.props.location.query.order || 'pulls';
    return (
        <FormGroup>
          <label>Order by:</label>{' '}
          <Radio name="boxOrder"
                 value="pulls"
                 checked={order === 'pulls'}
                 inline
                 onChange={this.onBoxOrderChange}
          >
            Downloads
          </Radio>
          {' '}
          <Radio name="boxOrder"
                 value="updated"
                 checked={order === 'updated'}
                 inline
                 onChange={this.onBoxOrderChange}
          >
            Last updated
          </Radio>
        </FormGroup>
    )
  };

  render() {
    this.activePage = parseInt(this.props.location.query.page || 1, 10);
    this.username = this.props.params.username;

    let pageTitle = 'All boxes';
    if (this.username) {
      pageTitle = `${this.username}'s boxes`
    } else if (this.props.location.query.q) {
      pageTitle = 'Search results'
    }
    return (
        <div>
          <PageHeader>{pageTitle}</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
          {this.renderOrderControls()}
          <div>
            <ListGroup>
              {this.renderBoxesList()}
            </ListGroup>
          </div>

          <div style={{textAlign: 'center'}}>
            {this.renderPagination()}
          </div>
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    boxes: state.entities.boxes,
    boxesPages: state.pagination.boxes[
        props.params.username || (props.location.query.q && '__search__') || '__all__'
    ],
  }
}

export default connect(mapStateToProps, {
  fetchBoxes: actions.loadBoxes,
})(BoxList)
