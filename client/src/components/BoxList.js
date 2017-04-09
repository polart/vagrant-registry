import React, {Component} from "react";
import { connect } from 'react-redux';
import { Pagination, ListGroup, ListGroupItem, PageHeader } from 'react-bootstrap';
import * as actions from "../actions";
import MyBreadcrumbs from "./MyBreadcrumbs";


class BoxList extends Component {
  componentWillMount() {
    this.props.fetchBoxes(null, this.props.location.query.page || 1);
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

  render() {
    this.activePage = parseInt(this.props.location.query.page || 1, 10);

    return (
        <div>
          <PageHeader>All Boxes</PageHeader>
          <MyBreadcrumbs router={this.props.router} />
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
