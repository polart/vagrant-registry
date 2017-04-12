import React, {Component} from "react";
import { connect } from 'react-redux';
import {Pagination, ListGroup, ListGroupItem, PageHeader, FormGroup, Radio} from 'react-bootstrap';
import Moment from "moment";
import * as actions from "../actions";
import MyBreadcrumbs from "./MyBreadcrumbs";


const ORDERING = {
  pulls: '-pulls',
  updated: '-date_updated',
};
const DEFAULT_ORDERING = ORDERING.pulls;


class BoxList extends Component {
  componentDidMount() {
    this.props.fetchBoxes(
        null,
        this.props.location.query.page || 1,
        ORDERING[this.props.location.query.orderBy] || DEFAULT_ORDERING
    );
  }

  onPageChange = (page) => {
    this.props.fetchBoxes(null, page);
    this.props.router.push(`/boxes/?page=${page}`);
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
    this.props.fetchBoxes(
        null,
        this.props.location.query.page,
        ORDERING[e.target.value]
    );

    const location = this.props.router.createLocation({
      pathname: this.props.router.location.pathname,
      query: {
        orderBy: e.target.value,
        page: this.props.location.query.page,
      }
    });
    this.props.router.push(location);
  };

  renderBoxesList = () => {
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
    if (this.props.boxesPages.count === 0) {
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
    const orderBy = this.props.location.query.orderBy || 'pulls';
    return (
        <FormGroup>
          <label>Order by:</label>{' '}
          <Radio name="boxOrder"
                 value="pulls"
                 checked={orderBy === 'pulls'}
                 inline
                 onChange={this.onBoxOrderChange}
          >
            Downloads
          </Radio>
          {' '}
          <Radio name="boxOrder"
                 value="updated"
                 checked={orderBy === 'updated'}
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

    return (
        <div>
          <PageHeader>All Boxes</PageHeader>
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

function mapStateToProps(state) {
  return {
    boxes: state.entities.boxes,
    boxesPages: state.pagination.boxes.__all,
  }
}

export default connect(mapStateToProps, {
  fetchBoxes: actions.loadBoxes,
})(BoxList)
